from typing import *

import pytest

from contextlib import contextmanager
from flask import template_rendered
from app import create_app, db, login
from config import config
from app.models import Wall, User, Investment, Worker


@contextmanager
def temp_db():
    db.create_all()
    try:
        yield db
    finally:
        db.session.remove()
        db.drop_all()


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
def wall_data() -> Dict:
    return {
        "sector": "G",
        "level": 2,
        "localization": "O/5",
        "brick_type": "YTONG",
        "wall_width": 25,
        "wall_length": 10.5,
        "floor_ord": 3.1,
        "ceiling_ord": 6.2,
    }


@pytest.fixture
def add_wall(app_and_db, wall_data):
    Wall.add_wall(**wall_data)


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
