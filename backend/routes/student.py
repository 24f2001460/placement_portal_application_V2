from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models.models import *
from datetime import datetime, timezone

from celery.result import AsyncResult

student_bp = Blueprint('student', __name__)

BRANCH_MAPPING = {
    'cse': ['cse', 'computer science', 'computer science and engineering'],
    'ece': ['ece', 'electronics', 'electronics and communication', 'electronics and communication engineering'],
    'me': ['me', 'mechanical', 'mechanical engineering'],
    'ce': ['ce', 'civil', 'civil engineering'],
    'ee': ['ee', 'electrical', 'electrical engineering']
}

def is_branch_eligible(student_branch_raw, eligible_branches_raw):
    if not eligible_branches_raw or len(eligible_branches_raw.strip()) == 0:
        return True
    student_branch = student_branch_raw.strip().lower()
    allowed_branches = [b.strip().lower() for b in eligible_branches_raw.split(',')]
    
    for allowed in allowed_branches:
        if allowed == student_branch:
            return True
        # Check mapping
        if student_branch in BRANCH_MAPPING:
            aliases = BRANCH_MAPPING[student_branch]
            if allowed in aliases or any(alias in allowed for alias in aliases):
                return True
    return False


# ─── Helper ──────────────────────────────────────────
def get_student_profile():
    email = get_jwt_identity()
    user = User.query.filter_by(email=email).first()
    if not user or user.role != 'student' or not user.is_active:
        return None
    student = StudentProfile.query.filter_by(user_id=user.id).first()
    if not student or student.status == 'blacklisted':
        return None
    return student

# ─── DASHBOARD ───────────────────────────────────────
@student_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    student = get_student_profile()
    if not student:
        return jsonify({'error': 'Student only or blocked!'}), 403

    applications = Application.query.filter_by(student_id=student.id).all()

    return jsonify({
        'id': student.id,
        'full_name': student.full_name,
        'roll_number': student.roll_number,
        'branch': student.branch,
        'cgpa': student.cgpa,
        'is_placed': student.is_placed,
        'total_applications': len(applications),
        'phone': student.phone,
        'skills': student.skills,
        'linkedin_url': student.linkedin_url,
        'github_url': student.github_url,
        'bio': student.bio,
        'resume_filename': student.resume_filename
    }), 200


# ─── ALL APPROVED DRIVES ─────────────────────────────
@student_bp.route('/drives', methods=['GET'])
@jwt_required()
def get_drives():
    student = get_student_profile()
    if not student:
        return jsonify({'error': 'Student only!'}), 403

    # Search filter
    search = request.args.get('search', '')
    eligible_only = request.args.get('eligible_only', 'false').lower() == 'true'

    drives = PlacementDrive.query.filter_by(status='approved').filter(
        PlacementDrive.job_title.ilike(f'%{search}%')
    ).all()

    result = []
    for d in drives:
        # Check already applied
        already_applied = Application.query.filter_by(
            student_id=student.id,
            drive_id=d.id
        ).first()

        # Eligibility check
        cgpa_eligible = student.cgpa >= d.min_cgpa
        backlogs_eligible = student.backlogs <= d.max_backlogs
        branch_eligible = is_branch_eligible(student.branch, d.eligible_branches)

        is_eligible = cgpa_eligible and backlogs_eligible and branch_eligible

        if eligible_only and not is_eligible:
            continue

        result.append({
            'id': d.id,
            'job_title': d.job_title,
            'company': d.company.company_name,
            'location': d.location,
            'salary_range': d.salary_range,
            'min_cgpa': d.min_cgpa,
            'eligible_branches': d.eligible_branches,
            'deadline': str(d.application_deadline),
            'already_applied': bool(already_applied),
            'is_eligible': is_eligible,
            'eligibility_reason': f"CGPA: {'Pass' if cgpa_eligible else 'Fail'}, Backlogs: {'Pass' if backlogs_eligible else 'Fail'}, Branch: {'Pass' if branch_eligible else 'Fail'}"
        })

    return jsonify(result), 200


# ─── APPLY FOR DRIVE ─────────────────────────────────
@student_bp.route('/drives/<int:drive_id>/apply', methods=['POST'])
@jwt_required()
def apply_drive(drive_id):
    student = get_student_profile()
    if not student:
        return jsonify({'error': 'Student only!'}), 403

    drive = PlacementDrive.query.get_or_404(drive_id)

    if drive.status != 'approved':
        return jsonify({'error': 'Drive not approved yet!'}), 400

    # Deadline check
    if datetime.now(timezone.utc) > drive.application_deadline.replace(tzinfo=timezone.utc):
        return jsonify({'error': 'Deadline passed!'}), 400

    # Already applied check
    existing = Application.query.filter_by(
        student_id=student.id,
        drive_id=drive_id
    ).first()
    if existing:
        return jsonify({'error': 'Already applied!'}), 409

    # Eligibility check
    if student.cgpa < drive.min_cgpa:
        return jsonify({'error': f'Minimum CGPA {drive.min_cgpa} needed!'}), 400
    if student.backlogs > drive.max_backlogs:
        return jsonify({'error': f'Maximum backlogs allowed is {drive.max_backlogs}!'}), 400
    if not is_branch_eligible(student.branch, drive.eligible_branches):
        return jsonify({'error': f'Branch not eligible. Eligible branches: {drive.eligible_branches}'}), 400

    data = request.get_json() or {}

    application = Application()
    application.student_id = student.id
    application.drive_id = drive_id
    application.status = 'applied'
    application.cover_letter = data.get('cover_letter', '')

    db.session.add(application)
    db.session.commit()

    try:
        from extensions import cache
        cache.delete('admin_applications')
    except Exception:
        pass

    return jsonify({'message': 'Successfully applied!'}), 201


# ─── MY APPLICATIONS ─────────────────────────────────
@student_bp.route('/applications', methods=['GET'])
@jwt_required()
def my_applications():
    student = get_student_profile()
    if not student:
        return jsonify({'error': 'Student only!'}), 403

    applications = Application.query.filter_by(student_id=student.id).all()

    result = []
    for app in applications:
        result.append({
            'application_id': app.id,
            'company': app.drive.company.company_name,
            'job_title': app.drive.job_title,
            'status': app.status,
            'applied_at': str(app.applied_at)
        })

    return jsonify(result), 200


# ─── UPDATE PROFILE ──────────────────────────────────
@student_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    student = get_student_profile()
    if not student:
        return jsonify({'error': 'Student only!'}), 403

    data = request.get_json()

    student.full_name = data.get('full_name', student.full_name)
    student.phone = data.get('phone', student.phone)
    student.skills = data.get('skills', student.skills)
    student.linkedin_url = data.get('linkedin_url', student.linkedin_url)
    student.github_url = data.get('github_url', student.github_url)
    student.bio = data.get('bio', student.bio)

    db.session.commit()

    return jsonify({'message': 'Profile updated!'}), 200
 #---------------------Export applications CSV────────────────────────────
@student_bp.route('/applications/export', methods=['POST'])
@jwt_required()
def export_applications():
    from tasks import export_applications_csv  # ← andar import
    student = get_student_profile()
    if not student:
        return jsonify({'error': 'Student only!'}), 403

    task = export_applications_csv.delay(student.id)
    return jsonify({
        'message': 'Export started!',
        'task_id': task.id
    }), 202


#---------------------Export status check────────────────────────────
@student_bp.route('/applications/export/status/<task_id>', methods=['GET'])
@jwt_required()
def export_status(task_id):
    task = AsyncResult(task_id)
    if task.state == 'PENDING':
        return jsonify({'status': 'processing'}), 200
    elif task.state == 'SUCCESS':
        return jsonify({'status': 'done', 'result': task.result}), 200
    else:
        return jsonify({'status': task.state}), 200


#---------------------Download exported CSV────────────────────────────
@student_bp.route('/applications/export/download/<int:student_id>', methods=['GET'])
@jwt_required()
def download_export(student_id):
    from flask import send_from_directory
    import os
    directory = os.path.abspath('exports')
    filename = f'applications_{student_id}.csv'
    return send_from_directory(directory, filename, as_attachment=True)


#---------------------Get companies list for students──────────────────
@student_bp.route('/companies', methods=['GET'])
@jwt_required()
def get_companies():
    student = get_student_profile()
    if not student:
        return jsonify({'error': 'Student only!'}), 403

    search = request.args.get('search', '')
    companies = CompanyProfile.query.filter(CompanyProfile.approval_status == 'approved').filter(
        CompanyProfile.company_name.ilike(f'%{search}%')
    ).all()

    result = []
    for c in companies:
        result.append({
            'id': c.id,
            'company_name': c.company_name,
            'hr_contact_name': c.hr_contact_name,
            'website': c.website,
            'industry': c.industry,
            'description': c.description,
            'headquarters': c.headquarters,
            'drives': [{
                'id': d.id,
                'job_title': d.job_title,
                'status': d.status,
                'deadline': str(d.application_deadline),
                'location': d.location,
                'salary_range': d.salary_range,
                'min_cgpa': d.min_cgpa,
                'eligible_branches': d.eligible_branches
            } for d in c.drives if d.status == 'approved']
        })
    return jsonify(result), 200


#---------------------Upload Resume────────────────────────────────────
@student_bp.route('/profile/resume', methods=['POST'])
@jwt_required()
def upload_resume():
    student = get_student_profile()
    if not student:
        return jsonify({'error': 'Student only!'}), 403

    if 'resume' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['resume']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not (file.filename.lower().endswith('.pdf') or file.filename.lower().endswith('.docx')):
        return jsonify({'error': 'Only PDF or DOCX allowed!'}), 400

    import os
    os.makedirs('uploads/resumes', exist_ok=True)
    filename = f"resume_{student.id}_{file.filename}"
    file_path = os.path.join('uploads/resumes', filename)
    file.save(file_path)

    student.resume_filename = filename
    db.session.commit()

    # Clear cache
    try:
        from extensions import cache
        cache.delete('admin_students')
    except Exception:
        pass

    return jsonify({'message': 'Resume uploaded successfully!', 'filename': filename}), 200


#---------------------View Resume──────────────────────────────────────
@student_bp.route('/profile/resume/view/<int:student_id>', methods=['GET'])
@jwt_required()
def view_resume(student_id):
    student = StudentProfile.query.get_or_404(student_id)
    if not student.resume_filename:
        return jsonify({'error': 'Resume not found!'}), 404

    from flask import send_from_directory
    import os
    directory = os.path.abspath('uploads/resumes')
    return send_from_directory(directory, student.resume_filename)


#---------------------Get Notifications────────────────────────────────
@student_bp.route('/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    student = get_student_profile()
    if not student:
        return jsonify({'error': 'Student only!'}), 403

    notifications = Notification.query.filter_by(user_id=student.user_id).order_by(Notification.created_at.desc()).all()
    result = []
    for n in notifications:
        result.append({
            'id': n.id,
            'title': n.title,
            'message': n.message,
            'is_read': n.is_read,
            'link': n.link,
            'created_at': str(n.created_at)
        })
    return jsonify(result), 200


#---------------------Read Notification────────────────────────────────
@student_bp.route('/notifications/<int:notif_id>/read', methods=['PUT'])
@jwt_required()
def read_notification(notif_id):
    student = get_student_profile()
    if not student:
        return jsonify({'error': 'Student only!'}), 403

    n = Notification.query.filter_by(id=notif_id, user_id=student.user_id).first_or_404()
    n.is_read = True
    db.session.commit()
    return jsonify({'message': 'Notification marked as read'}), 200
