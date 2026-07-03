from flask import Blueprint,request,jsonify
from flask_jwt_extended import create_access_token
from database import db
from models.models import *
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

auth_bp = Blueprint('auth',__name__)

# REGISTER STUDENT
@auth_bp.route('/register/student',methods=['POST'])
def register_student():

    data = request.get_json() or {}
    required_fields = ['email','password','full_name','roll_number','branch','year','cgpa']

    for i in required_fields:
        if not data.get(i):
            return jsonify({'error':f'{i} is required'}), 400

    email = data['email'].strip().lower()
    if User.query.filter_by(email=email).first():
        return jsonify({'error':'Email already registered'}),409
    roll_number = data['roll_number'].strip().lower()
    if StudentProfile.query.filter_by(roll_number=roll_number).first():
        return jsonify({'error':'Student with this roll number already registered'}),409

    try:
        user = User()
        user.email = email
        user.role = 'student'
        user.is_active = True
        user.set_passwd(data['password'])
        db.session.add(user)

        db.session.flush()

        profile = StudentProfile()
        profile.user_id = user.id
        profile.full_name = data['full_name'].strip()
        profile.roll_number = roll_number
        profile.branch = data['branch'].strip()
        profile.year = int(data['year'])
        profile.cgpa = float(data['cgpa'])
        db.session.add(profile)

        db.session.commit()
        try:
            from extensions import cache
            cache.delete('admin_students')
        except Exception:
            pass

        return jsonify({'message':'Student regsitered successfully'}),201

    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({'error':'Database error occurred'}),500

    except Exception:
        db.session.rollback()
        return jsonify({'error':'Registration Failed'}),500


#REGISTER COMPANY
@auth_bp.route('/register/company',methods=['POST'])
def register_company():
    data = request.get_json() or {}
    required_fields = ['email','password','company_name','hr_contact_name','hr_phone','industry']

    for i in required_fields:
        if not data.get(i):
            return jsonify({'error':f'{i} is required'}), 400

    email = data['email'].strip().lower()
    if User.query.filter_by(email=email).first():
        return jsonify({'error':'Email already registered'}),409
    company_name = data['company_name'].strip().lower()
    industry = data['industry'].strip().lower()
    if CompanyProfile.query.filter_by(company_name=company_name).first() and CompanyProfile.query.filter_by(industry=industry).first():
        return jsonify({'error':'This company already registered'}),409

    try:
        user = User()
        user.email = data['email']
        user.role = 'company'
        user.is_active = True
        user.set_passwd(data['password'])
        db.session.add(user)

        db.session.flush()

        company = CompanyProfile()
        company.user_id = user.id
        company.company_name = data.get('company_name', '')
        company.hr_contact_name = data.get('hr_contact_name', '')
        company.hr_phone = data.get('hr_phone', '')
        company.website = data.get('website', '')
        company.approval_status = 'pending'
        db.session.add(company)

        db.session.commit()
        try:
            from extensions import cache
            cache.delete('admin_companies')
        except Exception:
            pass
        return jsonify({'message': 'Details has been send successfully. Wait for admin approval'}), 201

    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({'error':'Database error occurred'}),500

    except Exception:
        db.session.rollback()
        return jsonify({'error':'Failed!, Try again'}),500


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error':'Email and Password are required'}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_passwd(password):
        return jsonify({'error': 'Wrong Credentials'}), 401

    if not user.is_active:
        return jsonify({'error': 'Credentials Deactivated'}), 403

    if user.role == 'company':
        cp = user.company_profile
        if cp:
            if cp.approval_status == 'pending':
                return jsonify({"error":"Company Approval is still pending"}), 403
            if cp.approval_status == 'rejected':
                 return jsonify({"error":"Company was not approved"}), 403
            if cp.approval_status == 'blacklisted':
                 return jsonify({"error":"Company has been blacklisted"}), 403

    # Last login
    user.last_login = datetime.now(timezone.utc)
    db.session.commit()

    # JWT token
    token = create_access_token(identity=user,additional_claims={'role':user.role})

    return jsonify({
        "message":"Login Successful!",
        "access_token":token,
        "user":{
            "id":user.id,
            "email":user.email,
            "role":user.role
        }
    }), 200


@auth_bp.route('/gchat/mock_webhook', methods=['POST'])
def mock_gchat_webhook():
    data = request.get_json() or {}
    print(f"\n[GCHAT WEBHOOK MOCK] Received notification:\n{data.get('text')}\n")
    return jsonify({'status': 'success', 'message': 'Mock webhook received data successfully!'}), 200


