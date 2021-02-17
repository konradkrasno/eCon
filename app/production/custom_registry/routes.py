from flask import render_template, redirect, url_for, request, g
from flask_login import login_required, current_user
from flask_wtf import FlaskForm

from app.production.custom_registry import bp
from app.production.custom_registry.forms import CreateTableForm, AddColumnForm
from app.production.custom_registry.registry import RegistryStore, Registry


@bp.route("/")
@login_required
def start():
    registries = RegistryStore.get_user_registries(g.current_invest.id, current_user.username)
    return render_template(
        "production/custom_registry/start.html", title="Custom Registry", registries=registries
    )


@bp.route("/create_table", methods=["GET", "POST"])
@login_required
def create_table():
    form = CreateTableForm(g.current_invest.id, current_user.username)
    if form.validate_on_submit():
        registry_name = form.table_name.data
        return redirect(url_for("custom_registry.add_column", registry_name=registry_name))
    return render_template(
        "production/custom_registry/form.html", title="Create Table", form=form
    )


@bp.route("/add_column", methods=["GET", "POST"])
@login_required
def add_column():
    registry_name = request.args.get("registry_name")
    form = AddColumnForm(g.current_invest.id, current_user.username, registry_name)
    if form.validate_on_submit():
        name = form.name.data
        data_type = form.data_type.data
        form.registry.add_field(name, data_type)
        return redirect(url_for("custom_registry.registry", registry_name=registry_name))
    return render_template(
        "production/custom_registry/form.html", title="Add Column", form=form
    )


@bp.route("/registry", methods=["GET", "POST"])
@login_required
def registry():
    registry_name = request.args.get("registry_name")
    reg = Registry(g.current_invest.id, current_user.username, registry_name)
    field_names = reg.get_fields()
    items = reg.get_items()
    return render_template(
        "production/custom_registry/registry.html", title=registry_name, field_names=field_names, items=items
    )


@bp.route("/add_data", methods=["GET", "POST"])
@login_required
def add_data():
    registry_name = request.args.get("registry_name")
    reg = Registry(g.current_invest.id, current_user.username, registry_name)
    ItemForm = type("ItemForm", (FlaskForm,), reg.get_form_fields())
    form = ItemForm()
    if form.validate_on_submit():
        reg.add_item(form.data)
        return redirect(url_for("custom_registry.registry", registry_name=registry_name))
    return render_template(
        "production/custom_registry/form.html", title="Add Data", form=form
    )


@bp.route("/edit_item", methods=["GET", "POST"])
@login_required
def edit_item():
    _id = request.args.get("_id")
    registry_name = request.args.get("registry_name")
    reg = Registry(g.current_invest.id, current_user.username, registry_name)
    ItemForm = type("ItemForm", (FlaskForm,), reg.get_form_fields())
    form = ItemForm()
    if form.validate_on_submit():
        reg.edit_item(_id, form.data)
        return redirect(url_for("custom_registry.registry", registry_name=registry_name))
    return render_template(
        "production/custom_registry/form.html", title="Add Data", form=form
    )


@bp.route("/delete_item", methods=["GET", "POST"])
@login_required
def delete_item():
    _id = request.args.get("_id")
    registry_name = request.args.get("registry_name")
    reg = Registry(g.current_invest.id, current_user.username, registry_name)
    reg.delete_item(_id)
    return redirect(url_for("custom_registry.registry", registry_name=registry_name))
