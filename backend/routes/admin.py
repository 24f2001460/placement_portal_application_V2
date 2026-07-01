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
            'website': c.website,
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
            'status': s.status,
            'is_placed': s.is_placed
        })
    return jsonify(result), 200


@admin_bp.route('/students/<int:student_id>/blacklist', methods=['PUT'])
@admin_required
def blacklist_student(student_id):
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
            'company': d.company.company_name,
            'status': d.status,
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
    return jsonify({
        'students': [{'id': s.id, 'name': s.full_name, 'roll': s.roll_number} for s in students],
        'companies': [{'id': c.id, 'name': c.company_name} for c in companies]
    }), 200
