from typing import *

from werkzeug.urls import url_parse
from flask import (
    render_template,
    flash,
    redirect,
    url_for,
    request,
)
from flask_login import login_user, logout_user, current_user
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegisterForm, EditProfileForm, ChangePasswordForm
from app.models import User
from flask_login import login_required


@bp.route("/login", methods=["GET", "POST"])
def login() -> str:
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if not user or not user.validate_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("auth.login"))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("main.index")
        return redirect(next_page)
    return render_template("auth/user_form.html", title="Log In", form=form)


@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.index"))


@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
        )
        db.session.add(user)
        db.session.commit()
        flash("You are now registered user!")
        return redirect(url_for("auth.login"))
    return render_template("auth/user_form.html", title="Register", form=form)


@bp.route("/edit", methods=["GET", "POST"])
@login_required
def edit_profile() -> str:
    form = EditProfileForm(username=current_user.username, email=current_user.email)
    if form.validate_on_submit():
        user = User.query.filter_by(username=current_user.username).first()
        if user:
            user.username = form.username.data
            user.email = form.email.data
            db.session.add(user)
            db.session.commit()
            flash("You change your profile data.")
            return redirect(url_for("main.user", user=current_user))
    return render_template("auth/user_form.html", title="Edit Profile", form=form)


@bp.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password() -> str:
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=current_user.username).first()
        if user:
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash("You change your password successfully.")
            return redirect(url_for("main.user", user=current_user))
    return render_template("auth/user_form.html", title="Change Password", form=form)
