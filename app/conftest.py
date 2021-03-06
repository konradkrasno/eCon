import datetime
import os
from contextlib import contextmanager
from typing import *

import pytest
from flask import template_rendered
from flask_login import AnonymousUserMixin

from app import create_app, db, login, r
from app.models import Wall, User, Investment, Worker, Task
from config import config, BASE_DIR

contexts_required = pytest.mark.skipif(
    not os.path.exists(os.path.join(BASE_DIR, config["UPLOAD_FOLDER"], "temp/test")),
    reason="contexts csv does not exist",
)


@contextmanager
def temp_db():
    db.create_all()
    try:
        yield db
    finally:
        db.session.remove()
        db.drop_all()
        r.flushdb()


@pytest.fixture
def app_and_db():
    config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
    config["TESTING"] = True
    config["WTF_CSRF_ENABLED"] = False
    config["MAIL_SERVER"] = "localhost"
    config["MAIL_PORT"] = 8025
    app = create_app(config)
    ctx = app.test_request_context()
    ctx.push()
    with app.app_context():
        with temp_db() as test_db:
            yield app, test_db
    ctx.pop()


@pytest.fixture
def client(app_and_db):
    with app_and_db[0].test_client() as client:
        yield client


@pytest.fixture
def captured_templates(app_and_db):
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))

    template_rendered.connect(record, app_and_db[0])
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app_and_db[0])


@pytest.fixture
def wall_data(add_investment) -> Dict:
    investment = Investment.query.first()
    return {
        "local_id": 1,
        "sector": "G",
        "level": 2,
        "localization": "O/5",
        "brick_type": "YTONG",
        "wall_width": 25,
        "wall_length": 10.5,
        "floor_ord": 3.1,
        "ceiling_ord": 6.2,
        "invest_id": investment.id,
    }


@pytest.fixture
def add_wall(app_and_db, wall_data):
    Wall.add_wall(**wall_data)


@pytest.fixture
def add_hole(app_and_db):
    Wall.add_hole(wall_id=1, width=1.2, height=2.25, amount=2)


@pytest.fixture
def add_processing(app_and_db):
    Wall.add_processing(wall_id=1, year=2020, month="December", done=0.4)


@pytest.fixture
def add_investment(app_and_db, active_user, unlogged_user):
    db = app_and_db[1]
    user1 = User.query.filter_by(username="active_user").first()
    user2 = User.query.filter_by(username="unlogged_user").first()
    investment = Investment(name="Test Invest", description="test text")
    worker1 = Worker(position="admin", admin=True, user_id=user1.id)
    worker2 = Worker(position="second worker", admin=False, user_id=user2.id)
    investment.workers.append(worker1)
    investment.workers.append(worker2)
    db.session.add(investment)
    db.session.commit()

    # setting current_invest
    investment = Investment.query.filter_by(name="Test Invest").first()
    user1.current_invest_id = investment.id
    db.session.commit()


@pytest.fixture
def add_tasks(app_and_db, add_investment):
    investment = Investment.query.first()
    worker1 = Worker.query.filter_by(position="admin").first()
    worker2 = Worker.query.filter_by(position="second worker").first()
    task1 = Task(
        description="test task 1",
        created_at=datetime.datetime.utcnow(),
        deadline=datetime.date.today() + datetime.timedelta(days=2),
        orderer=worker1,
        executor=worker2,
        progress=0,
        investment_id=investment.id,
    )
    task2 = Task(
        description="test task 2",
        created_at=datetime.datetime.utcnow(),
        deadline=datetime.date.today() + datetime.timedelta(days=2),
        orderer=worker1,
        executor=worker1,
        progress=0,
        investment_id=investment.id,
    )
    task3 = Task(
        description="test task 3",
        created_at=datetime.datetime.utcnow(),
        deadline=datetime.date.today() + datetime.timedelta(days=2),
        orderer=worker1,
        executor=worker1,
        progress=100,
        investment_id=investment.id,
    )
    db = app_and_db[1]
    db.session.add(task1)
    db.session.add(task2)
    db.session.add(task3)
    db.session.commit()


@pytest.fixture
def active_user(app_and_db):
    user = User(
        username="active_user", email="active_user@email.com", password="password"
    )
    user.is_active = True
    db.session.add(user)
    db.session.commit()


@pytest.fixture
def unlogged_user(app_and_db):
    user = User(
        username="unlogged_user",
        email="unlogged_user@email.com",
        password="password",
    )
    user.is_active = True
    db.session.add(user)
    db.session.commit()


@pytest.fixture
def inactive_user(app_and_db):
    user = User(
        username="inactive_user",
        email="inactive_user@email.com",
        password="password",
    )
    user.is_active = False
    db.session.add(user)
    db.session.commit()


@pytest.fixture
def test_with_authenticated_user(active_user):
    @login.request_loader
    def load_user_from_request(request):
        return User.query.filter(
            User.username.notin_(["unlogged_user", "inactive_user"])
        ).first()


@pytest.fixture
def test_with_anonymous_user():
    @login.request_loader
    def load_user_from_request(request):
        return AnonymousUserMixin()
