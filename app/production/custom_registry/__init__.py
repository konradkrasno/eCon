from flask import Blueprint

bp = Blueprint("custom_registry", __name__)

from app.production.custom_registry import routes
