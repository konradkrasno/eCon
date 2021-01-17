import glob

from werkzeug.utils import secure_filename
from flask import render_template, redirect, url_for, request, g, flash
from flask_login import login_required, current_user
from app.documents import bp
from app.documents.forms import NewFolderForm
from app.handling_files import remove, create_new_folder, get_user_path


@bp.route("/")
@login_required
def documents() -> str:
    user_path = get_user_path(current_user.id, g.current_invest.id)
    paths = glob.glob(user_path + "/*")
    return render_template("/documents/documents.html", title="Documents", paths=paths)


@bp.route("/new_folder", methods=["GET", "POST"])
def new_folder() -> str:
    if g.current_invest.id is None:
        flash("Choose investment first.")
        return redirect(url_for("investments.invest_list"))
    folder_path = request.args.get("folder_path")
    folder_abs_path = get_user_path(current_user.id, g.current_invest.id, folder_path)
    form = NewFolderForm(folder_abs_path)
    if form.validate_on_submit():
        create_new_folder(folder_abs_path, secure_filename(form.folder_name.data))
        flash("You created new folder successfully.")
        return redirect(url_for("documents.documents"))
    return render_template("documents/form.html", title="Create New Folder", form=form)


@bp.route("/delete", methods=["GET", "POST"])
def delete() -> str:
    path = request.args.get("path")
    remove(path)
    return redirect(url_for("documents.documents"))
