from flask import (
    render_template,
    redirect,
    url_for,
)
from flask_login import login_required, login_user
from app.main import bp
from app.models import User
from app.main.populate_db import populate_db


@bp.before_app_first_request
def before_first_request():
    if not User.query.filter_by(username="Guest").first():
        populate_db()


@bp.route("/")
@bp.route("/index")
@login_required
def index() -> str:
    return render_template("index.html", title="Home")


@bp.route("/schedule")
@login_required
def schedule() -> str:
    return render_template("in_preparation.html", title="Schedule")


@bp.route("/user/<string:username>")
@login_required
def user(username: str) -> str:
    user = User.query.filter_by(username=username).first()
    return render_template("user.html", title="Profile Page", user=user)


@bp.route("/guest", methods=["GET", "POST"])
def guest():
    user = User.query.filter_by(username="Guest").first()
    login_user(user, remember=True)
    return redirect(url_for("main.index"))
