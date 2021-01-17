from flask import (
    render_template,
    flash,
    redirect,
    url_for,
    request,
    g,
)
from werkzeug.utils import secure_filename
from flask_login import login_required, login_user
from config import config
from app.main import bp
from app.handling_files import save_file, handle_file
from app.models import Wall, User
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


@bp.route("/upload_files/<string:model>", methods=["GET", "POST"])
@login_required
def upload_files(model: str) -> str:
    if request.method == "POST":
        if not g.current_invest.id:
            flash("Choose investment first.")
            return redirect(url_for("investments.invest_list"))
        if "file[]" not in request.files:
            flash("No file part.")
            return redirect(request.url)
        temp = request.args.get("temp", False)
        catalog = request.args.get("catalog", "")
        files = request.files.getlist("file[]")
        for file in files:
            if file.filename == "":
                flash("No selected file.")
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                try:
                    save_file(file, filename, temp, catalog)
                except FileExistsError:
                    flash("File with this name already exists.")
                else:
                    messages = handle_file(filename, model, Wall)
                    for message in messages:
                        flash(message)
        next_url = request.args.get("next_url")
        if next_url is None:
            next_url = url_for("main.index")
        return redirect(next_url)
    return render_template("upload_file_form.html")


@bp.route("/guest", methods=["GET", "POST"])
def guest():
    user = User.query.filter_by(username="Guest").first()
    login_user(user, remember=True)
    return redirect(url_for("main.index"))
