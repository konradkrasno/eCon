web: flask db init; flask db migrate; flask db upgrade; gunicorn econ:app
worker: celery -A app.app_tasks.tasks.celery worker -l info
