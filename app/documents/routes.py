import os
import glob

from werkzeug.utils import secure_filename
from flask import render_template, redirect, url_for, request, g, flash
from flask_login import login_required, current_user
from app.documents import bp
from app.documents.forms import NewFolderForm
from app.main.forms import WarrantyForm
from app.handling_files import (
    remove,
    create_new_folder,
    get_metadata,
    get_current_and_prev_path,
)
from app.handling_files import allowed_file, save_file


@bp.route("/")
@login_required
def documents() -> str:
    current_path, prev_path = get_current_and_prev_path(
        request, current_user.id, g.current_invest.id
    )
    paths = glob.glob(current_path + "/*")
    files, folders = get_metadata(paths)
    return render_template(
        "/documents/documents.html",
        title="Documents",
        files=files,
        folders=folders,
        current_path=current_path,
        prev_path=prev_path,
    )


@bp.route("/new_folder", methods=["GET", "POST"])
@login_required
def new_folder() -> str:
    current_path, prev_path = get_current_and_prev_path(
        request, current_user.id, g.current_invest.id
    )
    form = NewFolderForm(current_path)
    if form.validate_on_submit():
        create_new_folder(current_path, secure_filename(form.folder_name.data))
        flash("You created new folder successfully.")
        return redirect(
            url_for(
                "documents.documents", current_path=current_path, prev_path=prev_path
            )
        )
    return render_template(
        "documents/form.html",
        title="Create New Folder",
        form=form,
        current_path=current_path,
    )


@bp.route("/upload_files", methods=["GET", "POST"])
@login_required
def upload_files():
    if request.method == "POST":
        current_path, prev_path = get_current_and_prev_path(
            request, current_user.id, g.current_invest.id
        )
        if "file[]" not in request.files:
            flash("No file part.")
            return redirect(request.url)
        files = request.files.getlist("file[]")
        for file in files:
            if file.filename == "":
                flash("No selected file.")
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                try:
                    save_file(
                        file,
                        current_path,
                        filename,
                    )
                except FileExistsError:
                    flash("File with this name already exists.")
                else:
                    flash("New file uploaded successfully.")
        return redirect(
            url_for(
                "documents.documents", current_path=current_path, prev_path=prev_path
            )
        )
    return render_template("upload_file_form.html")


@bp.route("/delete", methods=["GET", "POST"])
@login_required
def delete() -> str:
    form = WarrantyForm()
    if form.validate_on_submit():
        current_path, prev_path = get_current_and_prev_path(
            request, current_user.id, g.current_invest.id
        )
        if form.yes.data:
            filename = request.args.get("filename")
            file_path = os.path.join(current_path, filename)
            remove(file_path)
        return redirect(
            url_for(
                "documents.documents", current_path=current_path, prev_path=prev_path
            )
        )
    return render_template("warranty_form.html", title="Delete Item", form=form)


@bp.route("/download_file", methods=["GET", "POST"])
@login_required
def download_file():
    current_path, prev_path = get_current_and_prev_path(
        request, current_user.id, g.current_invest.id
    )
    # TODO finish
    return redirect(
        url_for("documents.documents", current_path=current_path, prev_path=prev_path)
    )


@bp.route("/download_files", methods=["GET", "POST"])
@login_required
def download_all_files():
    current_path, prev_path = get_current_and_prev_path(
        request, current_user.id, g.current_invest.id
    )
    # TODO finish
    return redirect(
        url_for("documents.documents", current_path=current_path, prev_path=prev_path)
    )
