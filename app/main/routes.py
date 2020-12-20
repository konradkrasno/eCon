from typing import *

import os
from flask import (
    render_template,
    flash,
    redirect,
    url_for,
    request,
)
from werkzeug.utils import secure_filename
from config import config
from app.main import bp
from app.main.forms import LoginForm
from app.models import User, Investment, Wall
from app.loading_csv import remove_file


@bp.route("/")
@bp.route("/index")
def index() -> str:
    user = {"username": "Konrad"}
    return render_template("index.html", title="Home", user=user)


@bp.route("/login", methods=["GET", "POST"])
def login() -> str:
    form = LoginForm()
    if form.validate_on_submit():
        flash("{}, you are logged in.".format(form.username.data))
        return redirect(url_for("main.index"))
    return render_template("login.html", title="Log In", form=form)


@bp.route("/tasks")
def tasks() -> str:
    return render_template("in_preparation.html", title="Tasks")


@bp.route("/team")
def team() -> str:
    return render_template("in_preparation.html", title="Team")


@bp.route("/production")
def production() -> str:
    return render_template("production/production.html", title="Production")


@bp.route("/documents")
def documents() -> str:
    return render_template("in_preparation.html", title="Documents")


@bp.route("/project")
def project() -> str:
    return render_template("in_preparation.html", title="Project")


@bp.route("/schedule")
def schedule() -> str:
    return render_template("in_preparation.html", title="Schedule")


def allowed_file(filename: str) -> bool:
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in config["ALLOWED_EXTENSIONS"]
    )


@bp.route("/upload_file/<string:model>", methods=["GET", "POST"])
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
