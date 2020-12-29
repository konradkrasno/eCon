from typing import *

from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from app import mail
from app.models import User
from app.auth.token import get_confirmation_token
from config import config


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(
    subject: str, sender: str, recipients: List, text_body: str, html_body: str
) -> None:
    msg = Message(subject=subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(
        target=send_async_email, args=(current_app._get_current_object(), msg)
    ).start()


def send_password_reset_confirmation(user: User) -> None:
    token = get_confirmation_token(id=user.id)
    send_email(
        "eCon - Reset Your Password",
        sender=config["MAIL_DEFAULT_SENDER"],
        recipients=[user.email],
        text_body=render_template("email/reset_password.txt", user=user, token=token),
        html_body=render_template("email/reset_password.html", user=user, token=token),
    )


def send_register_confirmation(user: User) -> None:
    token = get_confirmation_token(id=user.id)
    send_email(
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
    send_email(
        "eCon - Change Your Email Address",
        sender=config["MAIL_DEFAULT_SENDER"],
        recipients=[email],
        text_body=render_template("email/change_email.txt", user=user, token=token),
        html_body=render_template("email/change_email.html", user=user, token=token),
    )
