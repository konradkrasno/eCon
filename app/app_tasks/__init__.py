from celery import Celery, Task
from config import config
from app import create_app


CELERY_TASK_LIST = [
    "app.app_tasks.tasks",
]


def create_celery_app(app=None) -> Celery:
    """
    Create a new Celery object and tie together the Celery config to the app's config.
    Wrap all tasks in the request context.
    """
    app = app or create_app()
    celery = Celery(
        app.import_name, broker=config["broker_url"], include=CELERY_TASK_LIST
    )
    celery.conf.update(app.config)

    class ContextTask(Task):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return Task.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery
