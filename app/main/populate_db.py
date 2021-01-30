import os
from datetime import date, timedelta, datetime

import requests

from app import db
from app.app_tasks import tasks
from app.models import User, Investment, Worker, Task


def get_or_create_user(username: str, guest: bool = False) -> User:
    user = User.query.filter_by(username=username).first()
    if not user:
        user = User(
            username=username,
            email="{}@example.com".format(username.split()[-1].lower()),
            password="password123",
        )
        user.is_active = True
        db.session.add(user)
        db.session.commit()
        user = User.query.filter_by(username=username).first()
        if guest:
            tasks.delete_if_unused.apply_async(args=(user.id,), countdown=600)
    return user


def get_random_guest_name() -> str:
    response = requests.post(
        "https://random.api.randomkey.io/v1/name/full",
        headers={
            "auth": os.environ.get("RANDOMKEY_TOKEN"),
            "Content-Type": "application/json",
        },
        json={"gender": "0", "region": "us", "records": 1},
    )
    username = f"Guest ({datetime.utcnow().isoformat()})"
    if response.status_code == 200:
        name = response.json().get("name", None)
        if name:
            username = name
    return username


def populate_db() -> User:
    # Users
    guest = get_or_create_user(get_random_guest_name(), guest=True)
    user2 = get_or_create_user("Fryderyk Pawlak")
    user3 = get_or_create_user("Karina Tomaszewska")
    user4 = get_or_create_user("Jacek Chmiel")
    user5 = get_or_create_user("Honorata Wieczorek")

    # Workers
    worker1 = Worker(position="Visitor", admin=True, user_id=guest.id)
    worker2 = Worker(position="Site Manager", admin=True, user_id=user2.id)
    worker3 = Worker(position="Project Manager", admin=True, user_id=user3.id)
    worker4 = Worker(position="Site Engineer", admin=False, user_id=user4.id)
    worker5 = Worker(position="Quantity Engineer", admin=False, user_id=user5.id)

    # Tasks
    task1 = Task(
        description="Get to know eCon",
        deadline=date.today() + timedelta(days=2),
        priority=5,
        orderer=worker2,
        executor=worker1,
    )
    task2 = Task(
        description="Very important task",
        deadline=date.today() + timedelta(days=2),
        priority=5,
        orderer=worker2,
        executor=worker3,
    )
    task3 = Task(
        description="Less important task",
        deadline=date.today() + timedelta(days=1),
        priority=2,
        orderer=worker3,
        executor=worker2,
    )

    # Investment
    invest = Investment(
        name="Warsaw Skyscraper",
        description="Office building with reinforced concrete structure.",
    )
    invest.workers.append(worker1)
    invest.workers.append(worker2)
    invest.workers.append(worker3)
    invest.workers.append(worker4)
    invest.workers.append(worker5)
    invest.tasks.append(task1)
    invest.tasks.append(task2)
    invest.tasks.append(task3)
    db.session.add(invest)
    db.session.commit()

    return guest
