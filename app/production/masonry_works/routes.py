from typing import *

from flask import render_template, flash, redirect, url_for, request
from app.production.masonry_works import bp
from app.models import Hole, Processing, Wall
from app.production.masonry_works.forms import (
    AddWallForm,
    EditWallForm,
    HoleForm,
    ProcessingForm,
)
from app.main.forms import WarrantyForm
from app.production.masonry_works.data_treatment import TotalAreas, Categories


@bp.route("/masonry_works/walls")
def walls() -> str:
    sector = request.args.get("sector")
    level = request.args.get("level")
    localization = request.args.get("localization")
    brick_type = request.args.get("brick_type")
    wall_width = request.args.get("wall_width")
    items = Wall.query
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
    items = items.all()
    total = TotalAreas(items)
    return render_template(
        "production/masonry_works/walls.html",
        title="Walls",
        items=items,
        total=total,
        categories=Categories(Wall),
    )


@bp.route("/masonry_works/holes")
def holes() -> str:
    wall_id = request.args.get("wall_id")
    items = Hole.get_items_by_wall_id(wall_id)
    return render_template(
        "production/masonry_works/holes.html",
        title="Holes",
        items=items,
        wall_id=wall_id,
    )


@bp.route("/masonry_works/processing")
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


@bp.route("/masonry_works/modify")
def modify() -> str:
    wall_id = request.args.get("wall_id")
    item = Wall.query.filter_by(id=wall_id).first()
    return render_template(
        "production/masonry_works/modify.html", title="Modify", item=item
    )


@bp.route("/masonry_works/add_wall", methods=["GET", "POST"])
def add_wall() -> str:
    form = AddWallForm()
    if form.validate_on_submit():
        Wall.add_wall(**form.data)
        flash("You added a new wall.")
        return redirect(url_for("masonry_works.walls"))
    return render_template(
        "production/masonry_works/forms/wall_form.html", title="Add Wall", form=form
    )


@bp.route("/masonry_works/add_hole", methods=["GET", "POST"])
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


@bp.route("/masonry_works/add_processing", methods=["GET", "POST"])
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


@bp.route("/masonry_works/edit_wall", methods=["GET", "POST"])
def edit_wall() -> str:
    wall_id = request.args.get("wall_id")
    wall = Wall.query.filter_by(id=wall_id).first()
    form = EditWallForm(
        sector=wall.sector,
        level=wall.level,
        localization=wall.localization,
        brick_type=wall.brick_type,
        wall_width=wall.wall_width,
        wall_length=wall.wall_length,
        floor_ord=wall.floor_ord,
        ceiling_ord=wall.ceiling_ord,
    )
    if form.validate_on_submit():
        Wall.edit_wall(wall_id, **form.data)
        flash("You modified the wall.")
        return redirect(url_for("masonry_works.modify", wall_id=wall_id))
    return render_template(
        "production/masonry_works/forms/wall_form.html",
        title="Edit Wall",
        form=form,
    )


@bp.route("/masonry_works/edit_hole", methods=["GET", "POST"])
def edit_hole() -> str:
    wall_id = request.args.get("wall_id")
    hole_id = request.args.get("hole_id")
    hole = Hole.query.filter_by(id=hole_id).first()
    form = HoleForm(
        width=hole.width,
        height=hole.height,
        amount=hole.amount,
    )
    if form.validate_on_submit():
        Wall.edit_hole(hole_id, **form.data)
        flash("You modified the hole.")
        return redirect(url_for("masonry_works.holes", wall_id=wall_id))
    return render_template(
        "production/masonry_works/forms/hole_form.html",
        title="Edit Hole",
        form=form,
    )


@bp.route(
    "/masonry_works/edit_processing",
    methods=["GET", "POST"],
)
def edit_processing() -> str:
    wall_id = request.args.get("wall_id")
    proc_id = request.args.get("proc_id")
    processing = Processing.query.filter_by(id=proc_id).first()
    form = ProcessingForm(
        year=processing.year,
        month=processing.month,
        done=processing.done,
    )
    if form.validate_on_submit():
        Wall.edit_processing(proc_id, **form.data)
        flash("You modified the processing.")
        return redirect(url_for("masonry_works.processing", wall_id=wall_id))
    return render_template(
        "production/masonry_works/forms/processing_form.html",
        title="Edit Processing",
        form=form,
    )


@bp.route("/masonry_works/delete_wall", methods=["GET", "POST"])
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


@bp.route("/masonry_works/delete_hole", methods=["GET", "POST"])
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


@bp.route(
    "/masonry_works/delete_processing",
    methods=["GET", "POST"],
)
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
