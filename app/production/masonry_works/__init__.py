from flask import Blueprint

bp = Blueprint("masonry_works", __name__)

from app.production.masonry_works import forms, routes
