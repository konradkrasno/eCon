from datetime import date, timedelta

from sqlalchemy.exc import IntegrityError

from app import db, r
from app.app_tasks import tasks
from app.models import User, Investment, Worker, Task
from app.redis_client import (
    create_notification,
    add_notification,
    get_fake_name_from_buffer,
)


def get_or_create_user(username: str, guest: bool = False) -> User:
    user = User.query.filter_by(username=username).first()
    if user and guest:
        raise ValueError
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
            tasks.delete_if_unused.apply_async(args=(username,), countdown=600)
    return user


def populate_db() -> User:
    # Users
    while True:
        guest_name = get_fake_name_from_buffer(r)
        try:
            guest = get_or_create_user(guest_name, guest=True)
        except (IntegrityError, ValueError):
            db.session.rollback()
        else:
            break

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
    description = "Get to know eCon"
    task1 = Task(
        description=description,
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

    # Task notification
    notification = create_notification(
        worker_id=guest.workers.first().id,
        n_type="task",
        description=f"You have a new task: '{description}' from {user2.username}",
    )
    add_notification(r, notification)

    return guest
