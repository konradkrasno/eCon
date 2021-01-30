from flask import render_template

from app.app_tasks import tasks
from app.auth.token import get_confirmation_token
from app.models import User
from config import config


def send_password_reset_confirmation(user: User) -> None:
    token = get_confirmation_token(id=user.id)
    tasks.send_email.delay(
        "eCon - Reset Your Password",
        sender=config["MAIL_DEFAULT_SENDER"],
        recipients=[user.email],
        text_body=render_template("email/reset_password.txt", user=user, token=token),
        html_body=render_template("email/reset_password.html", user=user, token=token),
    )


def send_register_confirmation(user: User) -> None:
    token = get_confirmation_token(id=user.id)
    tasks.send_email.delay(
        "eCon - Activate Your Account",
        sender=config["MAIL_DEFAULT_SENDER"],
        recipients=[user.email],
        text_body=render_template("email/activate_account.txt", user=user, token=token),
        html_body=render_template(
            "email/activate_account.html", user=user, token=token
        ),
    )


def send_change_email_confirmation(email: str, user: User) -> None:
    token = get_confirmation_token(id=user.id, email=email)
    tasks.send_email.delay(
        "eCon - Change Your Email Address",
        sender=config["MAIL_DEFAULT_SENDER"],
        recipients=[email],
        text_body=render_template("email/change_email.txt", user=user, token=token),
        html_body=render_template("email/change_email.html", user=user, token=token),
    )


def send_complete_registration_mail(user: User) -> None:
    token = get_confirmation_token(id=user.id)
    tasks.send_email.delay(
        "eCon - Complete Registration",
        sender=config["MAIL_DEFAULT_SENDER"],
        recipients=[user.email],
        text_body=render_template(
            "email/complete_registration.txt", user=user, token=token
        ),
        html_body=render_template(
            "email/complete_registration.html", user=user, token=token
        ),
    )
