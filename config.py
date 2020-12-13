import os
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))


config = {
    "SECRET_KEY": os.environ.get("SECRET_KEY"),
    "SQLALCHEMY_DATABASE_URI": os.environ.get("DATABASE_URL")
    or "sqlite:///{}".format(os.path.join(BASE_DIR, "app.db")),
    "SQLALCHEMY_TRACK_MODIFICATIONS": False,
}
