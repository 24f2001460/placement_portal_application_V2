import os
import sys

# Ensure backend directory is in the Python path to resolve imports correctly
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from celery import Celery

def make_celery(app=None):
    celery = Celery(
        'placement_portal',
        broker='redis://localhost:6379/0',
        backend='redis://localhost:6379/0',
    )
    celery.conf.update(
        timezone='Asia/Kolkata',
        enable_utc=True,
    )

    if app:
        class ContextTask(celery.Task):
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return self.run(*args, **kwargs)
        celery.Task = ContextTask

    return celery

from tasks import celery