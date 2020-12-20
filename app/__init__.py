from flask import Flask
from config import config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap

db = SQLAlchemy()
migrate = Migrate()
bootstrap = Bootstrap()


def create_app(app_config=config):
    app = Flask(__name__)
    app.config.from_mapping(app_config)
    db.init_app(app)
    migrate.init_app(app, db)
    bootstrap.init_app(app)
    from app.production.masonry_works import bp as masonry_works_bp

    app.register_blueprint(masonry_works_bp)
    from app.main import bp as main_bp

    app.register_blueprint(main_bp)
    return app


from app import models
