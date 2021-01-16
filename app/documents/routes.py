import os, glob
from flask import render_template, redirect, url_for, request, current_app, g
from flask_login import login_required, current_user
from config import BASE_DIR
from app.documents import bp
from app.loading_csv import remove_file


@bp.route("/")
@login_required
def documents() -> str:
    files_dir = os.path.join(BASE_DIR, current_app.config["UPLOAD_FOLDER"])
    files = glob.glob(files_dir + "/*.pdf")
    return render_template("/documents/documents.html", title="Documents", files=files)


@bp.route("/new_folder", methods=["GET", "POST"])
def new_folder() -> str:
    return redirect(url_for("documents.documents"))


@bp.route("/delete", methods=["GET", "POST"])
def delete_file() -> str:
    filepath = request.args.get("filepath")
    remove_file(current_user.id, g.current_invest.id, filepath)
    return redirect(url_for("documents.documents"))
