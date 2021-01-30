from flask import (
    render_template,
    flash,
    redirect,
    url_for,
    request,
)
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy.exc import IntegrityError
from werkzeug.urls import url_parse

from app import db
from app.auth import bp
from app.auth import email
from app.auth.forms import (
    LoginForm,
    RegisterForm,
    EditProfileForm,
    ChangePasswordForm,
    ResetPasswordForm,
    CompleteRegistrationForm,
)
from app.auth.token import verify_token
from app.main.forms import WarrantyForm
from app.models import User


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
    return render_template("auth/form.html", title="Log In", form=form)


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
        email.send_register_confirmation(user)
        flash("Check your email to activate your account.")
        return redirect(url_for("auth.login"))
    return render_template("auth/form.html", title="Register", form=form)


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
    form = EditProfileForm(
        original_username=current_user.username, original_email=current_user.email
    )
    if form.validate_on_submit():
        user = User.query.filter_by(username=current_user.username).first()
        if user:
            user.username = form.username.data
            if form.email.data != current_user.email:
                email.send_change_email_confirmation(form.email.data, user)
                flash("Check your email to confirm the email address change.")
            db.session.commit()
            flash("You change your profile data.")
            return redirect(url_for("main.user", username=current_user.username))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template("auth/form.html", title="Edit Profile", form=form)


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
    return render_template("auth/form.html", title="Change Password", form=form)


@bp.route("/reset_password_request", methods=["GET", "POST"])
def reset_password_request() -> str:
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            email.send_password_reset_confirmation(user)
        flash("Check your email to reset your password.")
        return redirect(url_for("auth.login"))
    return render_template("auth/form.html", title="Reset Password", form=form)


@bp.route("/reset_password", methods=["GET", "POST"])
def reset_password() -> str:
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    token = request.args.get("token")
    _id = verify_token(token).get("id", None)
    user = User.get_user(_id)
    if not user:
        return redirect(url_for("main.index"))
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash("Your password has been reset.")
        return redirect(url_for("auth.login"))
    return render_template("auth/form.html", title="Change Password", form=form)


@bp.route("/complete_registration", methods=["GET", "POST"])
def complete_registration() -> str:
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    token = request.args.get("token")
    _id = verify_token(token).get("id", None)
    user = User.get_user(_id)
    if not user:
        return redirect(url_for("main.index"))
    form = CompleteRegistrationForm()
    if form.validate_on_submit():
        user.username = form.username.data
        user.set_password(form.password.data)
        user.is_active = True
        db.session.commit()
        flash("You have successfully complete the registration.")
        return redirect(url_for("auth.login"))
    return render_template("auth/form.html", title="Complete Registration", form=form)


@bp.route("/delete_account", methods=["GET", "POST"])
@login_required
def delete_account():
    username = request.args.get("username")
    form = WarrantyForm()
    if form.validate_on_submit():
        if form.no.data:
            return redirect(url_for("main.user", username=username))
        elif form.yes.data:
            user = User.query.filter_by(username=username).first()
            projects, empty_projects = User.check_admins(user_id=user.id)
            if projects:
                flash(
                    "This accounts is only admin in projects: {}."
                    " Give root permission to other user and try again".format(
                        [project.name for project in projects]
                    )
                )
                return redirect(url_for("main.user", username=username))
            workers = User.get_workers(user_id=user.id)
            if workers:
                for worker in workers:
                    db.session.delete(worker)
            if empty_projects:
                for project in empty_projects:
                    db.session.delete(project)
            db.session.delete(user)
            db.session.commit()
            flash("The account has been deleted.")
            return redirect(url_for("main.index"))
    return render_template("warranty_form.html", title="Delete Account", form=form)
