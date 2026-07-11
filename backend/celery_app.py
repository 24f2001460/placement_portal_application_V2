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
