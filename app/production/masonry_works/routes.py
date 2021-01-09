from flask import render_template, flash, redirect, url_for, request, g
from flask_login import login_required
from app.production.masonry_works import bp
from app.models import Hole, Processing, Wall
from app.production.masonry_works.forms import (
    WallForm,
    HoleForm,
    ProcessingForm,
)
from app.main.forms import WarrantyForm
from app.production.masonry_works.data_treatment import TotalAreas, Categories


@bp.route("/walls")
@login_required
def walls() -> str:
    sector = request.args.get("sector")
    level = request.args.get("level")
    localization = request.args.get("localization")
    brick_type = request.args.get("brick_type")
    wall_width = request.args.get("wall_width")
    items = Wall.get_all_items(g.current_invest.id)
    if sector:
        items = items.filter_by(sector=sector)
    if level:
        items = items.filter_by(level=level)
    if localization:
        items = items.filter_by(localization=localization)
    if brick_type:
        items = items.filter_by(brick_type=brick_type)
    if wall_width:
        items = items.filter_by(wall_width=wall_width)
    items = items.order_by("local_id").all()
    total = TotalAreas(items)
    return render_template(
        "production/masonry_works/walls.html",
        title="Walls",
        items=items,
        total=total,
        categories=Categories(Wall),
    )


@bp.route("/holes")
@login_required
def holes() -> str:
    wall_id = request.args.get("wall_id")
    items = Hole.get_items_by_wall_id(wall_id)
    return render_template(
        "production/masonry_works/holes.html",
        title="Holes",
        items=items,
        wall_id=wall_id,
    )


@bp.route("/processing")
@login_required
def processing() -> str:
    wall_id = request.args.get("wall_id")
    items = Processing.get_items_by_wall_id(wall_id)
    left_to_sale = Wall.get_left_to_sale(wall_id)
    return render_template(
        "production/masonry_works/processing.html",
        title="Processing",
        items=items,
        wall_id=wall_id,
        left_to_sale=left_to_sale,
    )


@bp.route("/modify")
@login_required
def modify() -> str:
    wall_id = request.args.get("wall_id")
    item = Wall.query.filter_by(id=wall_id).first()
    return render_template(
        "production/masonry_works/modify.html", title="Modify", item=item
    )


@bp.route("/add_wall", methods=["GET", "POST"])
@login_required
def add_wall() -> str:
    form = WallForm(g.current_invest.id)
    if form.validate_on_submit():
        Wall.add_wall(g.current_invest.id, **form.data)
        flash("You added a new wall.")
        return redirect(url_for("masonry_works.walls"))
    return render_template(
        "production/masonry_works/forms/wall_form.html", title="Add Wall", form=form
    )


@bp.route("/add_hole", methods=["GET", "POST"])
@login_required
def add_hole() -> str:
    wall_id = request.args.get("wall_id")
    form = HoleForm()
    if form.validate_on_submit():
        Wall.add_hole(wall_id, **form.data)
        flash("You added a new hole.")
        next_page = request.args.get("next_page")
        if not next_page:
            next_page = url_for("masonry_works.modify", wall_id=wall_id)
        return redirect(next_page)
    return render_template(
        "production/masonry_works/forms/hole_form.html", title="Add Hole", form=form
    )


@bp.route("/add_processing", methods=["GET", "POST"])
@login_required
def add_processing() -> str:
    wall_id = request.args.get("wall_id")
    form = ProcessingForm()
    if form.validate_on_submit():
        Wall.add_processing(wall_id, **form.data)
        flash("You added a new processing.")
        next_page = request.args.get("next_page")
        if not next_page:
            next_page = url_for("masonry_works.modify", wall_id=wall_id)
        return redirect(next_page)
    return render_template(
        "production/masonry_works/forms/processing_form.html",
        title="Add Processing",
        form=form,
    )


@bp.route("/edit_wall", methods=["GET", "POST"])
@login_required
def edit_wall() -> str:
    wall_id = request.args.get("wall_id")
    wall = Wall.query.filter_by(id=wall_id).first()
    form = WallForm(invest_id=g.current_invest.id, original_local_id=wall.local_id)
    if form.validate_on_submit():
        Wall.edit_wall(wall_id, **form.data)
        flash("You modified the wall.")
        return redirect(url_for("masonry_works.modify", wall_id=wall_id))
    elif request.method == "GET":
        form.local_id.data = wall.local_id
        form.sector.data = wall.sector
        form.level.data = wall.level
        form.localization.data = wall.localization
        form.brick_type.data = wall.brick_type
        form.wall_width.data = wall.wall_width
        form.wall_length.data = wall.wall_length
        form.floor_ord.data = wall.floor_ord
        form.ceiling_ord.data = wall.ceiling_ord
    return render_template(
        "production/masonry_works/forms/wall_form.html",
        title="Edit Wall",
        form=form,
    )


@bp.route("/edit_hole", methods=["GET", "POST"])
@login_required
def edit_hole() -> str:
    wall_id = request.args.get("wall_id")
    hole_id = request.args.get("hole_id")
    hole = Hole.query.filter_by(id=hole_id).first()
    form = HoleForm()
    if form.validate_on_submit():
        Wall.edit_hole(hole_id, **form.data)
        flash("You modified the hole.")
        return redirect(url_for("masonry_works.holes", wall_id=wall_id))
    elif request.method == "GET":
        form.width.data = hole.width
        form.height.data = hole.height
        form.amount.data = hole.amount
    return render_template(
        "production/masonry_works/forms/hole_form.html",
        title="Edit Hole",
        form=form,
    )


@bp.route("/edit_processing", methods=["GET", "POST"])
@login_required
def edit_processing() -> str:
    wall_id = request.args.get("wall_id")
    proc_id = request.args.get("proc_id")
    processing = Processing.query.filter_by(id=proc_id).first()
    form = ProcessingForm()
    if form.validate_on_submit():
        Wall.edit_processing(proc_id, **form.data)
        flash("You modified the processing.")
        return redirect(url_for("masonry_works.processing", wall_id=wall_id))
    elif request.method == "GET":
        form.year.data = processing.year
        form.month.data = processing.month
        form.done.data = processing.done
    return render_template(
        "production/masonry_works/forms/processing_form.html",
        title="Edit Processing",
        form=form,
    )


@bp.route("/delete_wall", methods=["GET", "POST"])
@login_required
def delete_wall() -> str:
    wall_id = request.args.get("wall_id")
    form = WarrantyForm()
    if form.validate_on_submit():
        if form.no.data:
            flash("Wall has not been deleted.")
            next_page = request.args.get("next_page")
            if not next_page:
                next_page = url_for("masonry_works.walls")
            return redirect(next_page)
        elif form.yes.data:
            Wall.delete_wall(wall_id)
            flash("Wall has been deleted.")
            return redirect(url_for("masonry_works.walls"))
    return render_template(
        "warranty_form.html",
        title="Delete Wall",
        form=form,
    )


@bp.route("/delete_hole", methods=["GET", "POST"])
@login_required
def delete_hole() -> str:
    wall_id = request.args.get("wall_id")
    hole_id = request.args.get("hole_id")
    form = WarrantyForm()
    if form.validate_on_submit():
        if form.no.data:
            flash("Hole has not been deleted.")
        elif form.yes.data:
            Wall.delete_hole(hole_id)
            flash("Hole has been deleted.")
        return redirect(url_for("masonry_works.holes", wall_id=wall_id))
    return render_template(
        "warranty_form.html",
        title="Delete Hole",
        form=form,
    )


@bp.route("/delete_processing", methods=["GET", "POST"])
@login_required
def delete_processing() -> str:
    wall_id = request.args.get("wall_id")
    proc_id = request.args.get("proc_id")
    form = WarrantyForm()
    if form.validate_on_submit():
        if form.no.data:
            flash("Processing has not been deleted.")
        elif form.yes.data:
            Wall.delete_processing(proc_id)
            flash("Processing has been deleted.")
        return redirect(url_for("masonry_works.processing", wall_id=wall_id))
    return render_template(
        "warranty_form.html",
        title="Delete Processing",
        form=form,
    )
