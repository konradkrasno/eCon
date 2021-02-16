import os

from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))


config = {
    "SECRET_KEY": os.environ.get("SECRET_KEY"),
    # Database settings
    "SQLALCHEMY_DATABASE_URI": os.environ.get("DATABASE_URL")
    or "sqlite:///{}".format(os.path.join(BASE_DIR, "app.db")),
    "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    # Mail settings
    "MAIL_DEFAULT_SENDER": os.environ.get("MAIL_DEFAULT_SENDER"),
    "MAIL_SERVER": os.environ.get("MAIL_SERVER"),
    "MAIL_PORT": os.environ.get("MAIL_PORT"),
    "MAIL_USE_TLS": os.environ.get("MAIL_USE_TLS") is not None,
    "MAIL_USERNAME": os.environ.get("MAIL_USERNAME"),
    "MAIL_PASSWORD": os.environ.get("MAIL_PASSWORD"),
    # Upload settings
    "UPLOAD_FOLDER": "app/static/files",
    "ALLOWED_EXTENSIONS": {"csv", "pdf"},
    # Celery settings
    "broker_url": os.environ.get("REDIS_URL"),
    "result_backend": os.environ.get("REDIS_URL"),
    # MongoDB settings
    "MONGO_URI": os.environ.get("MONGO_URI"),
}
