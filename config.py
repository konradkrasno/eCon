import os
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))


config = {
    "SECRET_KEY": os.environ.get("SECRET_KEY"),

    "SQLALCHEMY_DATABASE_URI": os.environ.get("DATABASE_URL")
    or "sqlite:///{}".format(os.path.join(BASE_DIR, "app_and_db.db")),
    "SQLALCHEMY_TRACK_MODIFICATIONS": False,

    "MAIL_DEFAULT_SENDER": os.environ.get("MAIL_DEFAULT_SENDER"),
    "MAIL_SERVER": os.environ.get("MAIL_SERVER"),
    "MAIL_PORT": os.environ.get("MAIL_PORT"),
    "MAIL_USE_TLS": os.environ.get("MAIL_USE_TLS") is not None,
    "MAIL_USERNAME": os.environ.get("MAIL_USERNAME"),
    "MAIL_PASSWORD": os.environ.get("MAIL_PASSWORD"),

    "UPLOAD_FOLDER": "app/static/files",
    "ALLOWED_EXTENSIONS": {"csv"},
}
