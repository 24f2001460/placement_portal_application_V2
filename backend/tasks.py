import os
import sys
import csv
from celery import Celery

def ensure_path():
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)



celery = Celery(
    'placement_portal',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0',
)
celery.conf.update(timezone='Asia/Kolkata', enable_utc=True)

@celery.task(name='tasks.export_applications_csv')
def export_applications_csv(student_id):
    ensure_path()
    from run import app
    from models.models import Application, StudentProfile, Notification
    from database import db
    with app.app_context():
        student = StudentProfile.query.get(student_id)
        if not student:
            return {'status': 'error', 'message': 'Student not found'}
        applications = Application.query.filter_by(student_id=student_id).all()
        os.makedirs('exports', exist_ok=True)
        filename = f'exports/applications_{student_id}.csv'
        with open(filename, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Student ID', 'Company Name', 'Drive Title', 'Status', 'Applied Date'])
            for a in applications:
                writer.writerow([
                    student.roll_number,
                    a.drive.company.company_name,
                    a.drive.job_title,
                    a.status,
                    str(a.applied_at)
                ])

        # Create alert in db
        try:
            notif = Notification(
                user_id=student.user_id,
                title="Applications Export Ready",
                message=f"Your placement application history export is ready. Click to download.",
                link=f"/api/student/applications/export/download/{student_id}"
            )
            db.session.add(notif)
            db.session.commit()
        except Exception as e:
            print(f'Notification error: {e}')

        try:
            from extensions import mail
            from flask_mail import Message
            msg = Message(
                subject='Your Application Export is Ready',
                recipients=[student.user.email],
                body=f'Hi {student.full_name},\n\nExport Ready\n\nFile: {filename}\n\nPlacement Portal\n\nThis is an automated message from the Placement Portal'
            )
            mail.send(msg)
        except Exception as e:
            print(f'Email error: {e}')

        return {'status': 'success', 'file': filename}


@celery.task(name='tasks.send_daily_reminders')
def send_daily_reminders():
    ensure_path()
    from run import app
    from extensions import mail
    from models.models import StudentProfile, PlacementDrive, Application
    from flask_mail import Message
    from datetime import datetime, timezone, timedelta
    import requests
    with app.app_context():
        now  = datetime.now(timezone.utc)
        soon = now + timedelta(days=3)
        drives = PlacementDrive.query.filter(
            PlacementDrive.status == 'approved',
            PlacementDrive.application_deadline >= now,
            PlacementDrive.application_deadline <= soon
        ).all()
        sent = 0
        gchat_msg_parts = []
        for drive in drives:
            gchat_msg_parts.append(f"- {drive.job_title} at {drive.company.company_name} (Deadline: {drive.application_deadline.strftime('%d %B %Y')})")
            students = StudentProfile.query.filter_by(is_placed=False).all()
            for student in students:
                already = Application.query.filter_by(
                    student_id=student.id, drive_id=drive.id).first()
                if not already:
                    try:
                        msg = Message(
                            subject=f'Reminder: {drive.job_title} deadline is approaching!',
                            recipients=[student.user.email],
                            body=f'Hi {student.full_name},\n\nDeadline for {drive.job_title} at {drive.company.company_name} is approaching on {drive.application_deadline.strftime("%d %B %Y")}!\n\nPlease apply soon!'
                        )
                        mail.send(msg)
                        sent += 1
                    except Exception as e:
                        print(f'Mail error: {e}')
                        
        gchat_url = app.config.get('GCHAT_WEBHOOK_URL')
        if gchat_url and gchat_msg_parts:
            gchat_payload = {
                "text": "⏰ *Upcoming Placement Deadlines Daily Reminder*:\n" + "\n".join(gchat_msg_parts)
            }
            try:
                requests.post(gchat_url, json=gchat_payload)
            except Exception as e:
                print(f"GChat Webhook error: {e}")
                
        return {'status': 'done', 'emails_sent': sent, 'gchat_sent': bool(gchat_msg_parts)}


@celery.task(name='tasks.send_monthly_report')
def send_monthly_report():
    ensure_path()
    from run import app
    from extensions import mail
    from models.models import StudentProfile, PlacementDrive, Application, User
    from flask_mail import Message
    from datetime import datetime, timezone, timedelta
    with app.app_context():
        now = datetime.now()
        first_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_last_month = first_this_month - timedelta(seconds=1)
        start_last_month = end_last_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        drives_conducted = PlacementDrive.query.filter(
            PlacementDrive.created_at >= start_last_month,
            PlacementDrive.created_at <= end_last_month
        ).count()
        
        students_applied = Application.query.filter(
            Application.applied_at >= start_last_month,
            Application.applied_at <= end_last_month
        ).count()
        
        students_selected = Application.query.filter(
            Application.status == 'selected',
            Application.selected_at >= start_last_month,
            Application.selected_at <= end_last_month
        ).count()

        total_drives   = PlacementDrive.query.count()
        total_students = StudentProfile.query.count()
        placed         = StudentProfile.query.filter_by(is_placed=True).count()
        total_apps     = Application.query.count()
        
        html = f'''<html><body>
        <h2>Monthly Placement Activity Report</h2>
        <p>Report Period: {start_last_month.strftime('%Y-%m-%d')} to {end_last_month.strftime('%Y-%m-%d')}</p>
        
        <h3>Monthly Activity (Last Month)</h3>
        <table border="1" cellpadding="8" style="border-collapse: collapse;">
          <tr style="background-color: #f2f2f2;"><th>Metric</th><th>Count</th></tr>
          <tr><td>Drives Conducted (Created)</td><td>{drives_conducted}</td></tr>
          <tr><td>Students Applied</td><td>{students_applied}</td></tr>
          <tr><td>Students Selected</td><td>{students_selected}</td></tr>
        </table>
        
        <h3>All-Time Cumulative Stats</h3>
        <table border="1" cellpadding="8" style="border-collapse: collapse; margin-top: 15px;">
          <tr style="background-color: #f2f2f2;"><th>Metric</th><th>Count</th></tr>
          <tr><td>Total Drives</td><td>{total_drives}</td></tr>
          <tr><td>Total Students</td><td>{total_students}</td></tr>
          <tr><td>Placed Students</td><td>{placed}</td></tr>
          <tr><td>Total Applications</td><td>{total_apps}</td></tr>
        </table>
        </body></html>'''
        
        admin = User.query.filter_by(role='admin').first()
        if admin:
            try:
                msg = Message(
                    subject='Monthly Placement Activity Report',
                    recipients=[app.config.get('MAIL_DEFAULT_SENDER', admin.email)],
                    html=html
                )
                mail.send(msg)
                return {'status': 'success'}
            except Exception as e:
                return {'status': 'error', 'message': str(e)}


from celery.schedules import crontab
celery.conf.beat_schedule = {
    'daily-reminders': {
        'task': 'tasks.send_daily_reminders',
        'schedule': crontab(hour=8, minute=0),
    },
    'monthly-report': {
        'task': 'tasks.send_monthly_report',
        'schedule': crontab(hour=9, minute=0, day_of_month=1),
    },
}