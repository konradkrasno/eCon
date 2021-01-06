import os
from flask import (
    render_template,
    flash,
    redirect,
    url_for,
    request,
)
from werkzeug.utils import secure_filename
from flask_login import current_user, login_required
from config import config
from app.main import bp
from app.loading_csv import remove_file
from app.models import Wall, User


@bp.route("/")
@bp.route("/index")
@login_required
def index() -> str:
    return render_template("index.html", title="Home")


@bp.route("/tasks")
@login_required
def tasks() -> str:
    return render_template("in_preparation.html", title="Tasks")


@bp.route("/production")
@login_required
def production() -> str:
    return render_template("production/production.html", title="Production")


@bp.route("/documents")
@login_required
def documents() -> str:
    return render_template("in_preparation.html", title="Documents")


@bp.route("/project")
@login_required
def project() -> str:
    return render_template("in_preparation.html", title="Project")


@bp.route("/schedule")
@login_required
def schedule() -> str:
    return render_template("in_preparation.html", title="Schedule")


@bp.route("/user/<string:username>")
@login_required
def user(username: str) -> str:
    user = User.query.filter_by(username=username).first()
    return render_template("user.html", title="Profile Page", user=user)


def allowed_file(filename: str) -> bool:
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in config["ALLOWED_EXTENSIONS"]
    )


@bp.route("/upload_file/<string:model>", methods=["GET", "POST"])
@login_required
def upload_file(model: str) -> str:
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files["file"]
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(config["UPLOAD_FOLDER"], filename))
            return redirect(
                url_for("main.uploaded_file", filename=filename, model=model)
            )
    return render_template("upload_file_form.html")


@bp.route("/uploads/<string:filename>/<string:model>")
@login_required
def uploaded_file(filename: str, model: str) -> str:
    messages = []
    if model == "walls":
        messages = Wall.upload_walls(filename)
    elif model == "holes":
        messages = Wall.upload_holes(filename)
    elif model == "processing":
        messages = Wall.upload_processing(filename)
    for message in messages:
        flash(message)
    remove_file(filename)
    return redirect(url_for("masonry_works.walls"))
