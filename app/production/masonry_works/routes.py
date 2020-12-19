from typing import *

import os
from flask import render_template, flash, redirect, url_for, request
from app.production.masonry_works import bp
from app.production.masonry_works.forms import WallForm, HoleForm, ProcessingForm
from app.main.forms import WarrantyForm
from app.models import Hole, Processing, Wall
from app.loading_csv import remove_file


@bp.route("/production/walls")
def walls() -> str:
    items = Wall.get_all_items()
    wall_header = Wall.get_header()
    return render_template(
        "production/masonry_works/walls.html",
        title="Walls",
        items=items,
        wall_header=wall_header,
    )


@bp.route("/production/holes/<int:wall_id>")
def holes(wall_id: int) -> str:
    items = Hole.get_items_by_wall_id(wall_id)
    hole_header = Hole.get_header()
    return render_template(
        "production/masonry_works/holes.html",
        title="Holes",
        items=items,
        hole_header=hole_header,
        wall_id=wall_id,
    )


@bp.route("/production/processing/<int:wall_id>")
def processing(wall_id: int) -> str:
    items = Processing.get_items_by_wall_id(wall_id)
    left_to_sale = Wall.get_left_to_sale(wall_id)
    processing_header = Processing.get_header()
    return render_template(
        "production/masonry_works/processing.html",
        title="Processing",
        items=items,
        processing_header=processing_header,
        wall_id=wall_id,
        left_to_sale=left_to_sale,
    )


@bp.route("/production/add_wall", methods=["GET", "POST"])
def add_wall() -> str:
    form = WallForm()
    if form.validate_on_submit():
        Wall.add_wall(**form.data)
        flash("You added a new wall.")
        return redirect(url_for("masonry_works.walls"))
    return render_template(
        "production/masonry_works/forms/wall_form.html", title="Add Wall", form=form
    )


@bp.route("/production/add_hole/<int:wall_id>", methods=["GET", "POST"])
def add_hole(wall_id: int) -> str:
    form = HoleForm()
    if form.validate_on_submit():
        Wall.add_hole(wall_id, **form.data)
        flash("You added a new hole.")
        next_page = request.args.get("next_page")
        if not next_page:
            next_page = url_for("masonry_works.walls")
        return redirect(next_page)
    return render_template(
        "production/masonry_works/forms/hole_form.html", title="Add Hole", form=form
    )


@bp.route("/production/add_processing/<int:wall_id>", methods=["GET", "POST"])
def add_processing(wall_id: int) -> str:
    form = ProcessingForm()
    if form.validate_on_submit():
        try:
            Wall.add_processing(wall_id, **form.data)
        except ValueError as e:
            form.done.errors.append(e)
        else:
            flash("You added a new processing.")
            next_page = request.args.get("next_page")
            if not next_page:
                next_page = url_for("masonry_works.walls")
            return redirect(next_page)
    return render_template(
        "production/masonry_works/forms/processing_form.html",
        title="Add Processing",
        form=form,
    )


@bp.route("/production/edit_wall/<int:wall_id>", methods=["GET", "POST"])
def edit_wall(wall_id: int) -> str:
    wall = Wall.query.filter_by(id=wall_id).first()
    form = WallForm(
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
        return redirect(url_for("masonry_works.walls"))
    return render_template(
        "production/masonry_works/forms/wall_form.html",
        title="Edit Wall",
        form=form,
    )


@bp.route("/production/edit_hole/<int:wall_id>/<int:hole_id>", methods=["GET", "POST"])
def edit_hole(wall_id: int, hole_id: int) -> str:
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
    "/production/edit_processing/<int:wall_id>/<int:proc_id>", methods=["GET", "POST"]
)
def edit_processing(wall_id: int, proc_id: int) -> str:
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


@bp.route("/production/delete_wall/<int:wall_id>", methods=["GET", "POST"])
def delete_wall(wall_id: int) -> str:
    form = WarrantyForm()
    if form.validate_on_submit():
        if form.no.data:
            flash("Wall has not been deleted.")
        elif form.yes.data:
            Wall.delete_wall(wall_id)
            flash("Wall has been deleted.")
        return redirect(url_for("masonry_works.walls"))
    return render_template(
        "warranty_form.html",
        title="Delete Wall",
        form=form,
    )


@bp.route(
    "/production/delete_hole/<int:wall_id>/<int:hole_id>", methods=["GET", "POST"]
)
def delete_hole(wall_id: int, hole_id: int) -> str:
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
    "/production/delete_processing/<int:wall_id>/<int:proc_id>",
    methods=["GET", "POST"],
)
def delete_processing(wall_id: int, proc_id: int) -> str:
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
