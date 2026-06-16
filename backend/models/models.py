from datetime import datetime, timezone
from database import db
from werkzeug.security import generate_password_hash,check_password_hash



class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime, nullable=True)

    # Relations
    student_profile = db.relationship(
        'StudentProfile',
        back_populates='user',
        uselist=False,
        cascade='all, delete-orphan'
    )

    company_profile = db.relationship(
        'CompanyProfile',
        back_populates='user',
        uselist=False,
        cascade='all, delete-orphan'
    )
    def set_passwd(self,p):
        self.password = generate_password_hash(p)
        
    def check_passwd(self,p):
        return check_password_hash(self.password,p)




class StudentProfile(db.Model):
    __tablename__ = 'student_profiles'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        unique=True,
        nullable=False
    )

    full_name = db.Column(db.String(150), nullable=False)
    roll_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)

    branch = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    cgpa = db.Column(db.Float, nullable=False)
    graduation_year = db.Column(db.Integer, nullable=True)
    backlogs = db.Column(db.Integer, default=0)

    resume_filename = db.Column(db.String(255), nullable=True)
    skills = db.Column(db.Text, nullable=True)
    linkedin_url = db.Column(db.String(300), nullable=True)
    github_url = db.Column(db.String(300), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    profile_photo = db.Column(db.String(255), nullable=True)

    status = db.Column(
        db.String(30),
        default='approved',
        nullable=False
    )

    is_placed = db.Column(db.Boolean, default=False)

    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relations
    user = db.relationship('User', back_populates='student_profile')

    applications = db.relationship(
        'Application',
        back_populates='student',
        cascade='all, delete-orphan'
    )




class CompanyProfile(db.Model):
    __tablename__ = 'company_profiles'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        unique=True,
        nullable=False
    )

    company_name = db.Column(db.String(200), nullable=False)
    hr_contact_name = db.Column(db.String(150), nullable=True)
    hr_phone = db.Column(db.String(20), nullable=True)
    website = db.Column(db.String(300), nullable=True)
    industry = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    logo_filename = db.Column(db.String(255), nullable=True)
    headquarters = db.Column(db.String(200), nullable=True)
    founded_year = db.Column(db.Integer, nullable=True)
    employee_count = db.Column(db.String(50), nullable=True)

    approval_status = db.Column(
        db.String(30),
        default='pending',
        nullable=False
    )

    rejection_reason = db.Column(db.Text, nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relations
    user = db.relationship('User', back_populates='company_profile')

    drives = db.relationship(
        'PlacementDrive',
        back_populates='company',
        cascade='all, delete-orphan'
    )




class PlacementDrive(db.Model):
    __tablename__ = 'placement_drives'

    id = db.Column(db.Integer, primary_key=True)

    company_id = db.Column(
        db.Integer,
        db.ForeignKey('company_profiles.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    job_title = db.Column(db.String(200), nullable=False)
    job_description = db.Column(db.Text, nullable=False)
    job_type = db.Column(db.String(30), default='full_time')
    location = db.Column(db.String(200), nullable=True)
    salary_range = db.Column(db.String(100), nullable=True)
    openings = db.Column(db.Integer, default=1)

    eligible_branches = db.Column(db.Text, nullable=True)
    min_cgpa = db.Column(db.Float, default=0.0)
    eligible_years = db.Column(db.Text, nullable=True)
    max_backlogs = db.Column(db.Integer, default=0)
    graduation_year = db.Column(db.Integer, nullable=True)

    required_skills = db.Column(db.Text, nullable=True)

    application_deadline = db.Column(db.DateTime, nullable=False)
    drive_date = db.Column(db.DateTime, nullable=True)

    status = db.Column(
        db.String(20),
        default='pending',
        nullable=False,
        index=True
    )

    rejection_reason = db.Column(db.Text, nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relations
    company = db.relationship('CompanyProfile', back_populates='drives')

    applications = db.relationship(
        'Application',
        back_populates='drive',
        cascade='all, delete-orphan'
    )



class Application(db.Model):
    __tablename__ = 'applications'

    __table_args__ = (
        db.UniqueConstraint(
            'student_id',
            'drive_id',
            name='unique_student_drive'
        ),
    )

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(
        db.Integer,
        db.ForeignKey('student_profiles.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    drive_id = db.Column(
        db.Integer,
        db.ForeignKey('placement_drives.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    status = db.Column(
        db.String(20),
        default='applied',
        nullable=False
    )

    applied_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    shortlisted_at = db.Column(db.DateTime, nullable=True)
    selected_at = db.Column(db.DateTime, nullable=True)
    rejected_at = db.Column(db.DateTime, nullable=True)

    interview_date = db.Column(db.DateTime, nullable=True)
    interview_mode = db.Column(db.String(50), nullable=True)
    interview_notes = db.Column(db.Text, nullable=True)

    cover_letter = db.Column(db.Text, nullable=True)
    company_remarks = db.Column(db.Text, nullable=True)
    offer_letter_filename = db.Column(db.String(255), nullable=True)
    package_offered = db.Column(db.String(100), nullable=True)

    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relations
    student = db.relationship('StudentProfile', back_populates='applications')

    drive = db.relationship('PlacementDrive', back_populates='applications')




class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    link = db.Column(db.String(300), nullable=True)

    # Relations
    user = db.relationship('User')




class ExportJob(db.Model):
    __tablename__ = 'export_jobs'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )

    task_id = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(20), default='pending')
    file_path = db.Column(db.String(300), nullable=True)

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    completed_at = db.Column(db.DateTime, nullable=True)
    error_message = db.Column(db.Text, nullable=True)

    # Relations
    user = db.relationship('User')