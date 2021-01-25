from datetime import date, timedelta
from app import db
from app.models import User, Investment, Worker, Task
from sqlalchemy.exc import IntegrityError


def populate_db() -> None:
    guest = User(username="Guest", email="guest@example.com", password="guest")
    guest.is_active = True
    db.session.add(guest)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()

    konrad = User(username="konrad", email="konrad@example.com", password="123")
    konrad.is_active = True
    db.session.add(konrad)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()

    ola = User(username="ola", email="ola@example.com", password="123")
    ola.is_active = True
    db.session.add(ola)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()

    guest = User.query.filter_by(username="Guest").first()
    konrad = User.query.filter_by(username="konrad").first()
    ola = User.query.filter_by(username="ola").first()

    worker1 = Worker(
        position="Advisor",
        admin=True,
        user_id=guest.id,
    )
    worker2 = Worker(position="Site Manager", admin=True, user_id=konrad.id)
    worker3 = Worker(position="Project Manager", admin=False, user_id=ola.id)

    task1 = Task(
        description="Very important task",
        deadline=date.today() + timedelta(days=2),
        priority=5,
        orderer=worker2,
        executor=worker3,
    )
    task2 = Task(
        description="Less important task",
        deadline=date.today() + timedelta(days=1),
        priority=2,
        orderer=worker3,
        executor=worker2,
    )

    invest = Investment(name="Bungalow", description="LA, California")
    invest.workers.append(worker1)
    invest.workers.append(worker2)
    invest.workers.append(worker3)
    invest.tasks.append(task1)
    invest.tasks.append(task2)
    db.session.add(invest)
    db.session.commit()
