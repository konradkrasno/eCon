from typing import *

import pytest

from contextlib import contextmanager
from flask import template_rendered
from app import create_app, db
from config import config
from app.models import Wall


def assert_flashes(client, expected_message, expected_category="message"):
    with client.session_transaction() as session:
        try:
            category, message = session["_flashes"][0]
        except KeyError:
            raise AssertionError("nothing flashed")
        assert expected_message in message
        assert expected_category == category


@contextmanager
def handle_db():
    db.create_all()
    try:
        yield db
    finally:
        db.session.remove()
        db.drop_all()


@pytest.fixture
def app():
    config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
    config["TESTING"] = True
    app = create_app(config)
    ctx = app.test_request_context()
    ctx.push()
    with app.app_context():
        with handle_db():
            yield app
    ctx.pop()


@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client


@pytest.fixture
def captured_templates(app):
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))

    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)


@pytest.fixture
def wall_data() -> Dict:
    return {
        "object": "G",
        "level": 2,
        "localization": "O/5",
        "brick_type": "YTONG",
        "wall_width": 25,
        "wall_length": 10.5,
        "floor_ord": 3.1,
        "ceiling_ord": 6.2,
    }


@pytest.fixture
def add_wall(app, wall_data):
    Wall.add_wall(**wall_data)
