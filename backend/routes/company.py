from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models.models import *
from datetime import datetime, timezone

company_bp = Blueprint('company', __name__)


# ─── Helper: Company check ───────────────────────────
def get_company_profile():
    email = get_jwt_identity()
    user = User.query.filter_by(email=email).first()
    if not user or user.role != 'company' or not user.is_active:
        return None
    company = CompanyProfile.query.filter_by(user_id=user.id).first()
    if not company or company.approval_status == 'blacklisted':
        return None
    return company

# ─── DASHBOARD ──────────────────────────────────────
@company_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    company = get_company_profile()
    if not company:
        return jsonify({'error': 'Company only or blocked!'}), 403

    if company.approval_status != 'approved':
        return jsonify({'error': 'Please wait for admin approval!'}), 403

    drives = PlacementDrive.query.filter_by(company_id=company.id).all()

    drives_data = []
    for d in drives:
        drives_data.append({
            'id': d.id,
            'job_title': d.job_title,
            'status': d.status,
            'deadline': str(d.application_deadline),
            'total_applicants': len(d.applications)
        })

    return jsonify({
        'company_name': company.company_name,
        'approval_status': company.approval_status,
        'total_drives': len(drives),
        'drives': drives_data
    }), 200


# ─── CREATE DRIVE ────────────────────────────────────
@company_bp.route('/drives', methods=['POST'])
@jwt_required()
def create_drive():
    company = get_company_profile()
    if not company:
        return jsonify({'error': 'Company only!'}), 403

    if company.approval_status != 'approved':
        return jsonify({'error': 'You can only create placement drives after admin approval!'}), 403

    data = request.get_json()

    if not data.get('job_title') or not data.get('job_description'):
        return jsonify({'error': 'Job title and description are required'}), 400

    if not data.get('application_deadline'):
        return jsonify({'error': 'Deadline is required'}), 400

    drive = PlacementDrive()
    drive.company_id = company.id
    drive.job_title = data.get('job_title')
    drive.job_description = data.get('job_description')
    drive.job_type = data.get('job_type', 'full_time')
    drive.location = data.get('location', '')
    drive.salary_range = data.get('salary_range', '')
    drive.openings = int(data.get('openings', 1))
    drive.eligible_branches = data.get('eligible_branches', '')
    drive.min_cgpa = float(data.get('min_cgpa', 0.0))
    drive.eligible_years = data.get('eligible_years', '')
    drive.max_backlogs = int(data.get('max_backlogs', 0))
    drive.required_skills = data.get('required_skills', '')
    
    # Handle deadline correctly
    deadline_str = data.get('application_deadline')
    try:
        drive.application_deadline = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
    except Exception:
        drive.application_deadline = datetime.strptime(deadline_str, "%Y-%m-%dT%H:%M")
        
    drive.status = 'pending'

    db.session.add(drive)
    db.session.commit()

    try:
        from extensions import cache
        cache.delete('admin_drives')
    except Exception:
        pass

    return jsonify({'message': 'Drive created! Please wait for admin approval.', 'drive_id': drive.id}), 201


# ─── COMPLETE DRIVE ──────────────────────────────────
@company_bp.route('/drives/<int:drive_id>/complete', methods=['PUT'])
@jwt_required()
def complete_drive(drive_id):
    company = get_company_profile()
    if not company:
        return jsonify({'error': 'Company only!'}), 403

    drive = PlacementDrive.query.filter_by(
        id=drive_id,
        company_id=company.id
    ).first()

    if not drive:
        return jsonify({'error': 'Drive not found!'}), 404

    drive.status = 'completed'
    db.session.commit()

    try:
        from extensions import cache
        cache.delete('admin_drives')
    except Exception:
        pass

    return jsonify({'message': f'Drive {drive.job_title} marked as completed!'}), 200


# ─── COMPANY DRIVES ───────────────────────────────────
@company_bp.route('/drives', methods=['GET'])
@jwt_required()
def get_drives():
    company = get_company_profile()
    if not company:
        return jsonify({'error': 'Company only!'}), 403

    drives = PlacementDrive.query.filter_by(company_id=company.id).all()

    result = []
    for d in drives:
        result.append({
            'id': d.id,
            'job_title': d.job_title,
            'job_description': d.job_description,
            'job_type': d.job_type,
            'location': d.location,
            'salary_range': d.salary_range,
            'status': d.status,
            'deadline': str(d.application_deadline),
            'min_cgpa': d.min_cgpa,
            'max_backlogs': d.max_backlogs,
            'eligible_branches': d.eligible_branches,
            'openings': d.openings,
            'required_skills': d.required_skills,
            'total_applicants': len(d.applications)
        })

    return jsonify(result), 200


# ─── GET DRIVE APPLICATIONS ──────────────────────────
@company_bp.route('/drives/<int:drive_id>/applications', methods=['GET'])
@jwt_required()
def get_applications(drive_id):
    company = get_company_profile()
    if not company:
        return jsonify({'error': 'Company only!'}), 403

    drive = PlacementDrive.query.filter_by(
        id=drive_id,
        company_id=company.id
    ).first()

    if not drive:
        return jsonify({'error': 'Drive not found!'}), 404

    applications = Application.query.filter_by(drive_id=drive_id).all()

    result = []
    for app in applications:
        result.append({
            'application_id': app.id,
            'student_id': app.student.id,
            'student_name': app.student.full_name,
            'roll_number': app.student.roll_number,
            'branch': app.student.branch,
            'cgpa': app.student.cgpa,
            'phone': app.student.phone,
            'backlogs': app.student.backlogs,
            'skills': app.student.skills,
            'linkedin_url': app.student.linkedin_url,
            'github_url': app.student.github_url,
            'bio': app.student.bio,
            'status': app.status,
            'applied_at': str(app.applied_at)
        })

    return jsonify(result), 200


# ─── UPDATE APPLICATION STATUS ───────────────────────
@company_bp.route('/applications/<int:app_id>/status', methods=['PUT'])
@jwt_required()
def update_status(app_id):
    company = get_company_profile()
    if not company:
        return jsonify({'error': 'Company only!'}), 403

    application = Application.query.get_or_404(app_id)

    # Check if this drive belongs to this company
    if application.drive.company_id != company.id:
        return jsonify({'error': 'Unauthorized!'}), 403

    data = request.get_json()
    new_status = data.get('status')

    valid_statuses = ['shortlisted', 'selected', 'rejected']
    if new_status not in valid_statuses:
        return jsonify({'error': f'Status must be one of: {valid_statuses}'}), 400

    application.status = new_status

    now = datetime.now(timezone.utc)
    if new_status == 'shortlisted':
        application.shortlisted_at = now
    elif new_status == 'selected':
        application.selected_at = now
        # Student placed mark
        application.student.is_placed = True
    elif new_status == 'rejected':
        application.rejected_at = now

    application.company_remarks = data.get('remarks', '')
    db.session.commit()

    try:
        from extensions import cache
        cache.delete('admin_applications')
        cache.delete('admin_students')
    except Exception:
        pass

    return jsonify({'message': f'Application {new_status}!'}), 200