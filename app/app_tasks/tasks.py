import os
import shutil
from datetime import datetime, timedelta
from time import sleep
from typing import *

from flask_mail import Message

from app import mail, db, r
from app.app_tasks import create_celery_app
from app.models import User, Investment
from app.redis_client import create_notification, add_notification

celery = create_celery_app()


@celery.task
def add(x, y):
    return x + y


@celery.task
def long_task(seconds: int):
    for i in range(seconds):
        print(i)
        sleep(1)


@celery.task
def archive_and_save(path: str, catalog: str, worker_id: int) -> None:
    catalog_path = os.path.join(path, catalog)
    shutil.make_archive(catalog_path, "zip", catalog_path)
    notification = create_notification(
        worker_id=worker_id,
        n_type="archive",
        description=f"You can download the file: {os.path.basename(catalog_path)}.zip",
    )
    add_notification(r, notification)


@celery.task
def send_email(
    subject: str, sender: str, recipients: List, text_body: str, html_body: str
) -> None:
    msg = Message(subject=subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)


@celery.task
def delete_if_unused(username: str) -> None:
    user = User.query.filter_by(username=username).first()
    if user:
        if user.last_activity + timedelta(seconds=300) < datetime.utcnow():
            for investment in Investment.get_by_user_id(user.id):
                db.session.delete(investment)
            db.session.delete(user)
            db.session.commit()
        else:
            delete_if_unused.apply_async(args=(user.id,), countdown=600)
