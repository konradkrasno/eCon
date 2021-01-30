from flask import render_template

from app.production.custom_registry import bp
from app.production.custom_registry.forms import CreateTableForm, CreateColumnForm


@bp.route("/")
def start():
    return render_template(
        "production/custom_registry/start.html", title="Custom Registry"
    )


@bp.route("/new_table", methods=["GET", "POST"])
def new_table():
    form = CreateTableForm()
    return render_template(
        "production/custom_registry/form.html", title="New Table", form=form
    )


@bp.route("/new_column", methods=["GET", "POST"])
def new_column():
    form = CreateColumnForm()
    return render_template(
        "production/custom_registry/form.html", title="New Column", form=form
    )
