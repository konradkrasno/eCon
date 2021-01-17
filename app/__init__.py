from flask import Flask
from config import config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail
from celery import Celery

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = "auth.login"
login.login_message = "Please log in to access this page."
mail = Mail()
bootstrap = Bootstrap()

CELERY_TASK_LIST = [
    "app.app_tasks.tasks",
]


def create_celery_app(app=None) -> Celery:
    """
    Create a new Celery object and tie together the Celery config to the app's config.
    Wrap all tasks in the context of the application.
    """
    app = app or create_app()
    celery = Celery(
        app.import_name, broker=config["broker_url"], include=CELERY_TASK_LIST
    )
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


def create_app(app_config=config) -> Flask:
    """
    Create a Flask application using the app factory pattern.
    """
    app = Flask(__name__)
    app.config.from_mapping(app_config)
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)

    from app.auth import bp as auth_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")

    from app.main import bp as main_bp

    app.register_blueprint(main_bp)

    from app.investments import bp as investments_bp

    app.register_blueprint(investments_bp, url_prefix="/investments")

    from app.team import bp as team_bp

    app.register_blueprint(team_bp, url_prefix="/team")

    from app.tasks import bp as tasks_bp

    app.register_blueprint(tasks_bp, url_prefix="/tasks")

    from app.documents import bp as documents_bp

    app.register_blueprint(documents_bp, url_prefix="/documents")

    from app.production.masonry_works import bp as masonry_works_bp

    app.register_blueprint(masonry_works_bp, url_prefix="/masonry_works")

    return app


from app import models
