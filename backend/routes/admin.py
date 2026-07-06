from flask import Blueprint,request,jsonify
from flask_jwt_extended import jwt_required,get_jwt_identity, get_current_user
from database import db
from models.models import *
from functools import wraps
from extensions import cache

admin_bp = Blueprint('admin',__name__)

def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if not user or user.role!='admin':
            return jsonify({'error':'Admin access required'}), 403
        return fn(*args,**kwargs)
    return wrapper



@admin_bp.route('/dashboard', methods=['GET'])
@admin_required
def dashboard():

    total_students = StudentProfile.query.count()
    total_companies = CompanyProfile.query.count()
    total_drives = PlacementDrive.query.count()
    pending_companies = CompanyProfile.query.filter_by(
        approval_status='pending'
    ).count()
    pending_drives = PlacementDrive.query.filter_by(
        status='pending'
    ).count()

    return jsonify({
        'total_students': total_students,
        'total_companies': total_companies,
        'total_drives': total_drives,
        'pending_companies': pending_companies,
        'pending_drives': pending_drives
    }), 200



@admin_bp.route('/companies', methods=['GET'])
@admin_required
@cache.cached(timeout=60, key_prefix='admin_companies')
def get_companies():
    companies = CompanyProfile.query.all()
    result = []
    for c in companies:
        result.append({
            'id': c.id,
            'company_name': c.company_name,
            'email': c.user.email,
            'hr_contact': c.hr_contact_name,
            'hr_phone': c.hr_phone,
            'website': c.website,
            'industry': c.industry,
            'description': c.description,
            'headquarters': c.headquarters,
            'founded_year': c.founded_year,
            'employee_count': c.employee_count,
            'approval_status': c.approval_status,
            'created_at': str(c.created_at)
        })
    return jsonify(result), 200




@admin_bp.route('/companies/<int:company_id>/approve', methods=['PUT'])
@admin_required
def approve_company(company_id):
    cache.delete('admin_companies')

    data = request.get_json()
    action = data.get('action')

    company = CompanyProfile.query.get_or_404(company_id)

    if action == 'approve':
        company.approval_status = 'approved'
        company.user.is_active = True
        db.session.commit()

        return jsonify({
            'message': f'{company.company_name} approved!'
        }), 200

    elif action == 'reject':
        company.approval_status = 'rejected'
        company.rejection_reason = data.get('reason', '')
        db.session.commit()

        return jsonify({
            'message': f'{company.company_name} rejected!'
        }), 200

    return jsonify({
        'error': 'Invalid action'
    }), 400




@admin_bp.route('/students', methods=['GET'])
@admin_required
@cache.cached(timeout=60, key_prefix='admin_students')
def get_students():
    students = StudentProfile.query.all()
    result = []
    for s in students:
        result.append({
            'id': s.id,
            'full_name': s.full_name,
            'email': s.user.email,
            'roll_number': s.roll_number,
            'branch': s.branch,
            'year': s.year,
            'cgpa': s.cgpa,
            'phone': s.phone,
            'date_of_birth': str(s.date_of_birth) if s.date_of_birth else None,
            'graduation_year': s.graduation_year,
            'backlogs': s.backlogs,
            'resume_filename': s.resume_filename,
            'skills': s.skills,
            'linkedin_url': s.linkedin_url,
            'github_url': s.github_url,
            'bio': s.bio,
            'status': s.status,
            'is_placed': s.is_placed
        })
    return jsonify(result), 200


@admin_bp.route('/students/<int:student_id>/blacklist', methods=['PUT'])
@admin_required
def blacklist_student(student_id):
    cache.delete('admin_students')
    try:
        cache.delete('admin_applications')
    except Exception:
        pass
    student = StudentProfile.query.get_or_404(student_id)
    student.status = 'blacklisted'
    student.user.is_active = False
    db.session.commit()
    return jsonify({'message': f'{student.full_name} blacklisted!'}), 200


@admin_bp.route('/drives', methods=['GET'])
@admin_required
@cache.cached(timeout=60, key_prefix='admin_drives')
def get_drives():
    drives = PlacementDrive.query.all()
    result = []
    for d in drives:
        result.append({
            'id': d.id,
            'job_title': d.job_title,
            'job_description': d.job_description,
            'job_type': d.job_type,
            'company': d.company.company_name,
            'location': d.location,
            'salary_range': d.salary_range,
            'openings': d.openings,
            'eligible_branches': d.eligible_branches,
            'min_cgpa': d.min_cgpa,
            'eligible_years': d.eligible_years,
            'max_backlogs': d.max_backlogs,
            'required_skills': d.required_skills,
            'status': d.status,
            'rejection_reason': d.rejection_reason,
            'deadline': str(d.application_deadline),
            'created_at': str(d.created_at)
        })
    return jsonify(result), 200


@admin_bp.route('/drives/<int:drive_id>/approve', methods=['PUT'])
@admin_required
def approve_drive(drive_id):
    cache.delete('admin_drives')
    data = request.get_json()
    action = data.get('action')
    drive = PlacementDrive.query.get_or_404(drive_id)
    if action == 'approve':
        drive.status = 'approved'
        db.session.commit()
        return jsonify({'message': f'{drive.job_title} approved!'}), 200
    elif action == 'reject':
        drive.status = 'rejected'
        drive.rejection_reason = data.get('reason', '')
        db.session.commit()
        return jsonify({'message': f'{drive.job_title} rejected!'}), 200
    return jsonify({'error': 'Invalid action'}), 400


@admin_bp.route('/drives/<int:drive_id>/complete', methods=['PUT'])
@admin_required
def complete_drive(drive_id):
    cache.delete('admin_drives')
    try:
        cache.delete('admin_applications')
    except Exception:
        pass
    drive = PlacementDrive.query.get_or_404(drive_id)
    drive.status = 'completed'
    db.session.commit()
    return jsonify({'message': f'{drive.job_title} marked as completed!'}), 200


@admin_bp.route('/search', methods=['GET'])
@admin_required
def search():
    query = request.args.get('q', '')
    students = StudentProfile.query.filter(
        StudentProfile.full_name.ilike(f'%{query}%') |
        StudentProfile.roll_number.ilike(f'%{query}%')
    ).all()
    companies = CompanyProfile.query.filter(
        CompanyProfile.company_name.ilike(f'%{query}%')
    ).all()
    drives = PlacementDrive.query.filter(
        PlacementDrive.job_title.ilike(f'%{query}%')
    ).all()
    return jsonify({
        'students': [{'id': s.id, 'full_name': s.full_name, 'roll_number': s.roll_number, 'branch': s.branch, 'cgpa': s.cgpa, 'status': s.status, 'is_placed': s.is_placed} for s in students],
        'companies': [{'id': c.id, 'company_name': c.company_name, 'email': c.user.email, 'hr_contact': c.hr_contact_name, 'website': c.website, 'approval_status': c.approval_status} for c in companies],
        'drives': [{'id': d.id, 'job_title': d.job_title, 'company': d.company.company_name, 'status': d.status, 'deadline': str(d.application_deadline)} for d in drives]
    }), 200


@admin_bp.route('/applications', methods=['GET'])
@admin_required
@cache.cached(timeout=60, key_prefix='admin_applications')
def get_applications():
    applications = Application.query.all()
    result = []
    for app in applications:
        result.append({
            'id': app.id,
            'student_id': app.student_id,
            'student_name': app.student.full_name,
            'student_email': app.student.user.email,
            'student_cgpa': app.student.cgpa,
            'student_phone': app.student.phone,
            'student_backlogs': app.student.backlogs,
            'student_skills': app.student.skills,
            'branch': app.student.branch,
            'roll_number': app.student.roll_number,
            'drive_id': app.drive_id,
            'job_title': app.drive.job_title,
            'company_name': app.drive.company.company_name,
            'cover_letter': app.cover_letter,
            'remarks': app.company_remarks,
            'status': app.status,
            'applied_at': str(app.applied_at)
        })
    return jsonify(result), 200


@admin_bp.route('/companies/<int:company_id>/blacklist', methods=['PUT'])
@admin_required
def blacklist_company(company_id):
    cache.delete('admin_companies')
    cache.delete('admin_drives')
    try:
        cache.delete('admin_applications')
    except Exception:
        pass
    company = CompanyProfile.query.get_or_404(company_id)
    company.approval_status = 'blacklisted'
    company.user.is_active = False

    # Cancel all its drives
    for drive in company.drives:
        drive.status = 'cancelled'

    db.session.commit()
    return jsonify({'message': f'{company.company_name} blacklisted and all its drives cancelled!'}), 200


@admin_bp.route('/students/<int:student_id>/activate', methods=['PUT'])
@admin_required
def activate_student(student_id):
    cache.delete('admin_students')
    try:
        cache.delete('admin_applications')
    except Exception:
        pass
    student = StudentProfile.query.get_or_404(student_id)
    student.status = 'approved'
    student.user.is_active = True
    db.session.commit()
    return jsonify({'message': f'{student.full_name} reactivated!'}), 200


@admin_bp.route('/drives/<int:drive_id>/cancel', methods=['PUT'])
@admin_required
def cancel_drive(drive_id):
    cache.delete('admin_drives')
    try:
        cache.delete('admin_applications')
    except Exception:
        pass
    drive = PlacementDrive.query.get_or_404(drive_id)
    drive.status = 'cancelled'
    db.session.commit()
    return jsonify({'message': f'{drive.job_title} drive cancelled!'}), 200
