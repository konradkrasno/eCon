from typing import *

from sqlalchemy.exc import IntegrityError
from werkzeug.urls import url_parse
from flask import (
    render_template,
    flash,
    redirect,
    url_for,
    request,
)
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.auth import bp
from app.auth.forms import (
    LoginForm,
    RegisterForm,
    EditProfileForm,
    ChangePasswordForm,
    ResetPasswordForm,
)
from app.models import User
from app.auth.token import verify_token
from app.auth.email import (
    send_password_reset_confirmation,
    send_register_confirmation,
    send_change_email_confirmation,
)


@bp.route("/login", methods=["GET", "POST"])
def login() -> str:
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if not user or not user.validate_password(form.password.data):
            flash("Invalid username or password.")
            return redirect(url_for("auth.login"))
        if not user.is_active:
            flash("Check your email to activate your account.")
            return redirect(url_for("auth.login"))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("main.index")
        return redirect(next_page)
    return render_template("auth/user_form.html", title="Log In", form=form)


@bp.route("/logout")
@login_required
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
        user = User.query.filter_by(username=form.username.data).first()
        send_register_confirmation(user)
        flash("Check your email to activate your account.")
        return redirect(url_for("auth.login"))
    return render_template("auth/user_form.html", title="Register", form=form)


@bp.route("/activate_account/<token>", methods=["GET", "POST"])
def activate_account(token: bytes) -> str:
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    _id = verify_token(token).get("id", None)
    user = User.get_user(_id)
    if user:
        user.is_active = True
        db.session.commit()
        flash("You have activated your account successfully.")
        return redirect(url_for("auth.login"))
    flash("The activation link is invalid.")
    return redirect(url_for("main.index"))


@bp.route("/edit", methods=["GET", "POST"])
@login_required
def edit_profile() -> str:
    form = EditProfileForm(username=current_user.username, email=current_user.email)
    if form.validate_on_submit():
        user = User.query.filter_by(username=current_user.username).first()
        if user:
            user.username = form.username.data
            if form.email.data != current_user.email:
                send_change_email_confirmation(form.email.data, user)
                flash("Check your email to confirm the email address change.")
            db.session.commit()
            flash("You change your profile data.")
            return redirect(url_for("main.user", username=current_user.username))
    return render_template("auth/user_form.html", title="Edit Profile", form=form)


@bp.route("/activate_email/<token>", methods=["GET", "POST"])
@login_required
def activate_email(token: bytes):
    token = verify_token(token)
    _id = token.get("id", None)
    email = token.get("email", None)
    if email:
        user = User.get_user(_id)
        if user == current_user:
            user.email = email
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                flash("You can not set this email address.")
            else:
                flash("You confirm your new email address.")
    else:
        flash("The email changing link is invalid.")
    return redirect(url_for("main.user", username=current_user.username))


@bp.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password() -> str:
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=current_user.username).first()
        if user:
            user.set_password(form.password.data)
            db.session.commit()
            flash("You change your password successfully.")
            return redirect(url_for("main.user", username=current_user.username))
    return render_template("auth/user_form.html", title="Change Password", form=form)


@bp.route("/reset_password_request", methods=["GET", "POST"])
def reset_password_request() -> str:
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_confirmation(user)
        flash("Check your email to reset your password.")
        return redirect(url_for("auth.login"))
    return render_template("auth/user_form.html", title="Reset Password", form=form)


@bp.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token: bytes) -> str:
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    _id = verify_token(token).get("id", None)
    user = User.get_user(_id)
    if not user:
        return redirect(url_for("main.index"))
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash("Your password has benn reset.")
        return redirect(url_for("auth.login"))
    return render_template("auth/user_form.html", title="Change Password", form=form)