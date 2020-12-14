from typing import *

from flask import render_template, flash, redirect, url_for, request
from app import app
from app.forms import LoginForm, WallForm, HoleForm, ProcessingForm
from app.models import User, Investment, Hole, Processing, Wall
from app.loading_csv import read_file


@app.route("/")
@app.route("/index")
def index() -> str:
    user = {"username": "Konrad"}
    return render_template("index.html", title="Home", user=user)


@app.route("/login", methods=["GET", "POST"])
def login() -> str:
    form = LoginForm()
    if form.validate_on_submit():
        flash("{}, you are logged in.".format(form.username.data))
        return redirect(url_for("index"))
    return render_template("login.html", title="Sign In", form=form)


@app.route("/tasks")
def tasks() -> str:
    return render_template("in_preparation.html", title="Tasks")


@app.route("/team")
def team() -> str:
    return render_template("in_preparation.html", title="Team")


@app.route("/production")
def production() -> str:
    return render_template("production/production.html")


@app.route("/production/walls")
def walls() -> str:
    items = Wall.get_all_items()
    wall_header = Wall.get_header()
    return render_template(
        "production/masonry_works/walls.html",
        title="Walls",
        items=items,
        wall_header=wall_header,
    )


@app.route("/production/holes/<int:wall_id>")
def holes(wall_id: int) -> str:
    items = Hole.get_all_items(wall_id)
    hole_header = Hole.get_header()
    return render_template(
        "production/masonry_works/holes.html",
        title="Holes",
        items=items,
        hole_header=hole_header,
        wall_id=wall_id,
    )


@app.route("/production/processing/<int:wall_id>")
def processing(wall_id: int) -> str:
    items = Processing.get_all_items(wall_id)
    processing_header = Processing.get_header()
    return render_template(
        "production/masonry_works/processing.html",
        title="Processing",
        items=items,
        processing_header=processing_header,
        wall_id=wall_id,
    )


@app.route("/production/add_wall", methods=["GET", "POST"])
def add_wall() -> str:
    form = WallForm()
    if form.validate_on_submit():
        Wall.add_item(**form.data)
        flash("You added a new wall.")
        return redirect(url_for("walls"))
    return render_template(
        "production/masonry_works/forms/wall_form.html", title="Wall Form", form=form
    )


@app.route("/production/add_hole/<int:wall_id>", methods=["GET", "POST"])
def add_hole(wall_id: int) -> str:
    form = HoleForm()
    if form.validate_on_submit():
        Wall.add_hole(wall_id, **form.data)
        flash("You added a new hole.")
        next_page = request.args.get("next_page")
        if not next_page:
            next_page = url_for("walls")
        return redirect(next_page)
    return render_template(
        "production/masonry_works/forms/hole_form.html", title="Hole Form", form=form
    )


@app.route("/production/add_processing/<int:wall_id>", methods=["GET", "POST"])
def add_processing(wall_id: int) -> str:
    form = ProcessingForm()
    if form.validate_on_submit():
        Wall.add_processing(wall_id, **form.data)
        flash("You added a new processing.")
        next_page = request.args.get("next_page")
        if not next_page:
            next_page = url_for("walls")
        return redirect(next_page)
    return render_template(
        "production/masonry_works/forms/processing_form.html",
        title="Processing Form",
        form=form,
    )


@app.route("/production/masonry_edit_form/<int:wall_id>", methods=["GET", "POST"])
def masonry_edit_form(wall_id: int) -> str:
    return render_template("in_preparation.html")


@app.route("/documents")
def documents() -> str:
    return render_template("in_preparation.html", title="Documents")


@app.route("/project")
def project() -> str:
    return render_template("in_preparation.html", title="Project")


@app.route("/schedule")
def schedule() -> str:
    return render_template("in_preparation.html", title="Schedule")
