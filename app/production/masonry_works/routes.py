from typing import *

from flask import render_template, flash, redirect, url_for, request
from app.production.masonry_works import bp
from app.production.masonry_works.forms import WallForm, HoleForm, ProcessingForm
from app.models import Hole, Processing, Wall


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
        "production/masonry_works/forms/wall_form.html", title="Wall Form", form=form
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
        "production/masonry_works/forms/hole_form.html", title="Hole Form", form=form
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
        title="Processing Form",
        form=form,
    )


@bp.route("/production/edit_masonry_item/<int:wall_id>", methods=["GET", "POST"])
def edit_masonry_item(wall_id: int) -> str:
    return render_template("in_preparation.html")
