from typing import *

import pytest

from contextlib import contextmanager
from flask import template_rendered
from app import create_app, db
from config import config
from app.models import Wall, User


def assert_flashes(client, expected_message, expected_category="message"):
    with client.session_transaction() as session:
        try:
            category, message = session["_flashes"][0]
        except KeyError:
            raise AssertionError("nothing flashed")
        assert expected_message in message
        assert expected_category == category


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
def add_user(app_and_db):
    user = User(username="test_user", email="test@email.com", password="password")
    user.is_active = True
    db.session.add(user)
    db.session.commit()
