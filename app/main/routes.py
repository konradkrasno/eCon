from typing import *

from flask import render_template, flash, redirect, url_for
from app.main import bp
from app.main.forms import LoginForm
from app.models import User, Investment
from app.loading_csv import read_file


@bp.route("/")
@bp.route("/index")
def index() -> str:
    user = {"username": "Konrad"}
    return render_template("index.html", title="Home", user=user)


@bp.route("/login", methods=["GET", "POST"])
def login() -> str:
    form = LoginForm()
    if form.validate_on_submit():
        flash("{}, you are logged in.".format(form.username.data))
        return redirect(url_for("main.index"))
    return render_template("login.html", title="Sign In", form=form)


@bp.route("/tasks")
def tasks() -> str:
    return render_template("in_preparation.html", title="Tasks")


@bp.route("/team")
def team() -> str:
    return render_template("in_preparation.html", title="Team")


@bp.route("/production")
def production() -> str:
    return render_template("production/production.html")


@bp.route("/documents")
def documents() -> str:
    return render_template("in_preparation.html", title="Documents")


@bp.route("/project")
def project() -> str:
    return render_template("in_preparation.html", title="Project")


@bp.route("/schedule")
def schedule() -> str:
    return render_template("in_preparation.html", title="Schedule")
