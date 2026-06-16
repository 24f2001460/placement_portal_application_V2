from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models.models import *
from datetime import datetime, timezone

student_bp = Blueprint('student', __name__)


# ─── Helper ──────────────────────────────────────────
def get_student_profile():
    email = get_jwt_identity()
    user = User.query.filter_by(email=email).first()
    if not user or user.role != 'student':
        return None
    student = StudentProfile.query.filter_by(user_id=user.id).first()
    return student

# ─── DASHBOARD ───────────────────────────────────────
@student_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    student = get_student_profile()
    if not student:
        return jsonify({'error': 'Student only!'}), 403

    applications = Application.query.filter_by(student_id=student.id).all()

    return jsonify({
        'full_name': student.full_name,
        'roll_number': student.roll_number,
        'branch': student.branch,
        'cgpa': student.cgpa,
        'is_placed': student.is_placed,
        'total_applications': len(applications)
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

        result.append({
            'id': d.id,
            'job_title': d.job_title,
            'company': d.company.company_name,
            'location': d.location,
            'salary_range': d.salary_range,
            'min_cgpa': d.min_cgpa,
            'eligible_branches': d.eligible_branches,
            'deadline': str(d.application_deadline),
            'already_applied': bool(already_applied)
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
        return jsonify({'error': 'Drive approved nahi hai!'}), 400

    # Deadline check
    if datetime.now(timezone.utc) > drive.application_deadline.replace(tzinfo=timezone.utc):
        return jsonify({'error': 'Deadline pass ho gayi!'}), 400

    # Already applied check
    existing = Application.query.filter_by(
        student_id=student.id,
        drive_id=drive_id
    ).first()
    if existing:
        return jsonify({'error': 'Already apply kar chuke ho!'}), 409

    # Eligibility check
    if student.cgpa < drive.min_cgpa:
        return jsonify({'error': f'Minimum CGPA {drive.min_cgpa} chahiye!'}), 400

    data = request.get_json() or {}

    application = Application()
    application.student_id = student.id
    application.drive_id = drive_id
    application.status = 'applied'
    application.cover_letter = data.get('cover_letter', '')

    db.session.add(application)
    db.session.commit()

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