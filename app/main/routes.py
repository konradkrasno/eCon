from flask import render_template, redirect, url_for, g, jsonify, request
from flask_login import login_required, login_user, current_user

from app import db, r
from app.main import bp
from app.main.populate_db import populate_db
from app.models import User, Worker
from app.redis_client import get_notification, add_fake_names_to_buffer


@bp.before_app_first_request
def before_first_request():
    add_fake_names_to_buffer(r)


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.update_last_activity()
        g.current_invest = current_user.get_current_invest()
        g.current_worker = Worker.get_by_username(
            g.current_invest.id, current_user.username
        )


@bp.route("/count_notifications")
@login_required
def count_notifications() -> str:
    n_type = request.args.get("n_type")
    return jsonify(g.current_worker.count_unseen_notifications(n_type=n_type))


@bp.route("/notifications")
@login_required
def notifications() -> str:
    worker_id = request.args.get("worker_id")
    notification = get_notification(r, worker_id)
    return jsonify([notification])


@bp.route("/")
@bp.route("/index")
@login_required
def index() -> str:
    coming_tasks = g.current_worker.get_coming_tasks()
    return render_template("index.html", title="Home", coming_tasks=coming_tasks)


@bp.route("/tutorial")
@login_required
def tutorial() -> str:
    return render_template("tutorial.html", title="Tutorial")


@bp.route("/schedule")
@login_required
def in_preparation() -> str:
    return render_template("in_preparation.html", title="Schedule")


@bp.route("/user/<string:username>")
@login_required
def user(username: str) -> str:
    user = User.query.filter_by(username=username).first()
    return render_template("user.html", title="Profile Page", user=user)


@bp.route("/guest", methods=["GET", "POST"])
def login_as_guest():
    guest = populate_db()
    login_user(guest, remember=True)
    return redirect(url_for("main.index"))


@bp.app_errorhandler(404)
def not_found_error(error):
    return render_template("404.html"), 404


@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template("500.html"), 500
