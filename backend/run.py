from flask import Flask
from database import db
from config import Config
from flask_cors import CORS
from models.models import *
from security import jwt
from extensions import cache, mail

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    jwt.init_app(app)
    cache.init_app(app)
    mail.init_app(app)
    CORS(app)

    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.company import company_bp
    from routes.student import student_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(company_bp, url_prefix='/api/company')
    app.register_blueprint(student_bp, url_prefix='/api/student')

    app.app_context().push()
    return app

def create_admin():
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        admin = User(
            email="admin@placement.com",
            role="admin",
            is_active=True
        )
        admin.set_passwd('admin123')
        db.session.add(admin)
        db.session.commit()

app = create_app()

def __seed():
    print("Seeding database with dummy data...")
    # Clear existing tables
    db.drop_all()
    db.create_all()
    
    # 1. Create Admin
    create_admin()
    
    # 2. Create Student Users and Profiles
    from datetime import datetime, timedelta
    
    # Student 1: Amit Sharma (ECE, Year 4, CGPA 9.1, 0 backlogs)
    u_amit = User(email="amit@placement.com", role="student", is_active=True)
    u_amit.set_passwd("password123")
    db.session.add(u_amit)
    db.session.flush()
    p_amit = StudentProfile(
        id=u_amit.id,
        user_id=u_amit.id,
        full_name="Amit Sharma",
        roll_number="10210345",
        phone="9876543211",
        date_of_birth=datetime(2004, 5, 12).date(),
        branch="ECE",
        year=4,
        cgpa=9.1,
        graduation_year=2026,
        backlogs=0,
        resume_filename="resume_amit.pdf",
        skills="Python, C++, Embedded Systems, Verilog",
        linkedin_url="https://linkedin.com/in/amitsharma",
        github_url="https://github.com/amitsharma",
        bio="Passionate about hardware-software codesign and embedded systems engineering.",
        status="approved"
    )
    db.session.add(p_amit)
    
    # Student 2: Priya Patel (CSE, Year 4, CGPA 8.4, 0 backlogs)
    u_priya = User(email="priya@placement.com", role="student", is_active=True)
    u_priya.set_passwd("password123")
    db.session.add(u_priya)
    db.session.flush()
    p_priya = StudentProfile(
        id=u_priya.id,
        user_id=u_priya.id,
        full_name="Priya Patel",
        roll_number="10210398",
        phone="9876543212",
        date_of_birth=datetime(2004, 8, 22).date(),
        branch="CSE",
        year=4,
        cgpa=8.4,
        graduation_year=2026,
        backlogs=0,
        resume_filename="resume_priya.pdf",
        skills="Java, Spring Boot, Vue.js, PostgreSQL",
        linkedin_url="https://linkedin.com/in/priyapatel",
        github_url="https://github.com/priyapatel",
        bio="Aspiring full-stack software development engineer focused on web technologies.",
        status="approved"
    )
    db.session.add(p_priya)
    
    # Student 3: Rahul Verma (ME, Year 3, CGPA 7.2, 1 backlog)
    u_rahul = User(email="rahul@placement.com", role="student", is_active=True)
    u_rahul.set_passwd("password123")
    db.session.add(u_rahul)
    db.session.flush()
    p_rahul = StudentProfile(
        id=u_rahul.id,
        user_id=u_rahul.id,
        full_name="Rahul Verma",
        roll_number="10220412",
        phone="9876543213",
        date_of_birth=datetime(2005, 2, 10).date(),
        branch="ME",
        year=3,
        cgpa=7.2,
        graduation_year=2027,
        backlogs=1,
        skills="CAD, SolidWorks, MATLAB, Thermodynamics",
        bio="Mechanical engineer interested in robotics systems and product design.",
        status="approved"
    )
    db.session.add(p_rahul)

    # Student 4: Sneha Gupta (CSE, Year 4, CGPA 6.8, 2 backlogs)
    u_sneha = User(email="sneha@placement.com", role="student", is_active=True)
    u_sneha.set_passwd("password123")
    db.session.add(u_sneha)
    db.session.flush()
    p_sneha = StudentProfile(
        id=u_sneha.id,
        user_id=u_sneha.id,
        full_name="Sneha Gupta",
        roll_number="10210214",
        phone="9876543214",
        date_of_birth=datetime(2004, 11, 30).date(),
        branch="CSE",
        year=4,
        cgpa=6.8,
        graduation_year=2026,
        backlogs=2,
        skills="HTML, CSS, JavaScript, Bootstrap",
        bio="UI/UX design and frontend web enthusiast.",
        status="approved"
    )
    db.session.add(p_sneha)

    # 3. Create Companies
    # Company 1: Google India (Approved)
    u_google = User(email="google@placement.com", role="company", is_active=True)
    u_google.set_passwd("password123")
    db.session.add(u_google)
    db.session.flush()
    p_google = CompanyProfile(
        id=u_google.id,
        user_id=u_google.id,
        company_name="Google India",
        hr_contact_name="Sundar Pichai",
        hr_phone="9999999991",
        website="https://google.com",
        industry="Tech",
        description="Google LLC is an American multinational technology company that focuses on artificial intelligence, search engine, online advertising, cloud computing, computer software, quantum computing, e-commerce, and consumer electronics.",
        headquarters="Mountain View, California",
        founded_year=1998,
        employee_count=150000,
        approval_status="approved"
    )
    db.session.add(p_google)

    # Company 2: Tata Consultancy Services (Approved)
    u_tcs = User(email="tcs@placement.com", role="company", is_active=True)
    u_tcs.set_passwd("password123")
    db.session.add(u_tcs)
    db.session.flush()
    p_tcs = CompanyProfile(
        id=u_tcs.id,
        user_id=u_tcs.id,
        company_name="Tata Consultancy Services",
        hr_contact_name="Rajesh Gopinathan",
        hr_phone="9999999992",
        website="https://tcs.com",
        industry="IT Services",
        description="Tata Consultancy Services (TCS) is an Indian multinational information technology services and consulting company headquartered in Mumbai.",
        headquarters="Mumbai, Maharashtra",
        founded_year=1968,
        employee_count=600000,
        approval_status="approved"
    )
    db.session.add(p_tcs)

    # Company 3: Startup Labs (Pending)
    u_startup = User(email="startup@placement.com", role="company", is_active=False)
    u_startup.set_passwd("password123")
    db.session.add(u_startup)
    db.session.flush()
    p_startup = CompanyProfile(
        id=u_startup.id,
        user_id=u_startup.id,
        company_name="Startup Labs",
        hr_contact_name="Alan Turing",
        hr_phone="9999999993",
        website="https://startuplabs.ai",
        industry="AI",
        description="A stealth startup working on developer-first agent automation tools.",
        headquarters="Remote",
        founded_year=2025,
        employee_count=10,
        approval_status="pending"
    )
    db.session.add(p_startup)

    db.session.commit()

    # 4. Create Placement Drives
    # Drive 1: Software Engineer at Google India (Approved)
    d_google = PlacementDrive(
        company_id=u_google.id,
        job_title="Software Engineer",
        job_description="Develop and optimize complex distributed systems. Write production-ready, clean C++/Python code.",
        job_type="Full-Time",
        location="Bangalore, Karnataka",
        salary_range="24 LPA",
        openings=5,
        eligible_branches="CSE, ECE",
        min_cgpa=8.5,
        eligible_years="4",
        max_backlogs=0,
        required_skills="Data Structures, Algorithms, Python/C++",
        application_deadline=datetime.utcnow() + timedelta(days=2),
        status="approved"
    )
    db.session.add(d_google)

    # Drive 2: Associate Consultant at TCS (Approved)
    d_tcs = PlacementDrive(
        company_id=u_tcs.id,
        job_title="Associate Consultant",
        job_description="Analyze business processes, collaborate with development teams, and present consultancy solutions to global clients.",
        job_type="Full-Time",
        location="Pune, Maharashtra",
        salary_range="7 LPA",
        openings=50,
        eligible_branches="CSE, ECE, ME",
        min_cgpa=6.5,
        eligible_years="3, 4",
        max_backlogs=1,
        required_skills="Communication, Analytical Thinking, basic SQL",
        application_deadline=datetime.utcnow() + timedelta(days=3),
        status="approved"
    )
    db.session.add(d_tcs)

    # Drive 3: Research Intern at Startup Labs (Pending)
    d_startup = PlacementDrive(
        company_id=u_startup.id,
        job_title="Research Intern (Generative AI)",
        job_description="Perform research on large-language model training, agent architectures, and prompt tuning frameworks.",
        job_type="Internship",
        location="Remote",
        salary_range="15 LPA equivalent",
        openings=2,
        eligible_branches="CSE",
        min_cgpa=8.0,
        eligible_years="4",
        max_backlogs=0,
        required_skills="PyTorch, Transformers, Deep Learning",
        application_deadline=datetime.utcnow() + timedelta(days=5),
        status="pending"
    )
    db.session.add(d_startup)

    db.session.commit()

    # 5. Create Applications
    # Amit (ECE, CGPA 9.1) applies to Google Software Engineer (min CGPA 8.5) -> eligible and applied
    app_amit = Application(
        student_id=u_amit.id,
        drive_id=d_google.id,
        status="shortlisted",
        cover_letter="I am very passionate about hardware architectures and software systems at Google.",
        applied_at=datetime.utcnow() - timedelta(hours=12)
    )
    db.session.add(app_amit)

    # Priya (CSE, CGPA 8.4) applies to TCS (min CGPA 6.5) -> eligible and selected
    app_priya = Application(
        student_id=u_priya.id,
        drive_id=d_tcs.id,
        status="selected",
        cover_letter="Excited to apply my web engineering and Spring Boot skills at TCS.",
        company_remarks="Strong performance in interviews. Offered role.",
        applied_at=datetime.utcnow() - timedelta(days=1)
    )
    db.session.add(app_priya)
    p_priya.is_placed = True

    # Rahul (ME, CGPA 7.2) applies to TCS (min CGPA 6.5) -> eligible and applied
    app_rahul = Application(
        student_id=u_rahul.id,
        drive_id=d_tcs.id,
        status="applied",
        cover_letter="Hoping to contribute with my analytical and programming skills.",
        applied_at=datetime.utcnow() - timedelta(hours=6)
    )
    db.session.add(app_rahul)

    db.session.commit()
    print("Database seeding completed successfully!")


if __name__ == "__main__":
    import sys
    db.create_all()
    create_admin()
    if len(sys.argv) > 1 and sys.argv[1] == '--seed':
        __seed()
    else:
        app.run()
