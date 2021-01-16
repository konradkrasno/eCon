from flask import (
    render_template,
    flash,
    redirect,
    url_for,
    request,
    g,
)
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user, login_user
from config import config
from app.main import bp
from app.loading_csv import save_file, remove_file
from app.models import Wall, User
from app.main.populate_db import populate_db


@bp.before_app_first_request
def before_first_request():
    populate_db()

@bp.route("/")
@bp.route("/index")
@login_required
def index() -> str:
    return render_template("index.html", title="Home")


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
        if not g.current_invest.id:
            flash("Choose investment first.")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save_file(file, current_user.id, g.current_invest.id, filename)
            return redirect(
                url_for("main.uploaded_file", filename=filename, model=model)
            )
    return render_template("upload_file_form.html")


@bp.route("/uploads/<string:filename>/<string:model>")
@login_required
def uploaded_file(filename: str, model: str) -> str:
    if not g.current_invest.id:
        flash("Choose investment first.")
        return redirect(request.url)
    messages = []
    if model == "walls":
        messages = Wall.upload_walls(g.current_invest.id, filename)
    elif model == "holes":
        messages = Wall.upload_holes(g.current_invest.id, filename)
    elif model == "processing":
        messages = Wall.upload_processing(g.current_invest.id, filename)
    elif model == "new_file":
        messages = ["New file uploaded successfully."]
    for message in messages:
        flash(message)
    if model == "new_file":
        return redirect(url_for("documents.documents"))
    remove_file(current_user.id, g.current_invest.id, filename)
    return redirect(url_for("masonry_works.walls"))


@bp.route("/guest", methods=["GET", "POST"])
def guest():
    user = User.query.filter_by(username="Guest").first()
    login_user(user, remember=True)
    return redirect(url_for("main.index"))
