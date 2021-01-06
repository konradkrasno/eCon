import pytest

from flask import url_for
from app.models import User


def test_index(client, captured_templates, test_with_authenticated_user):
    response = client.get(url_for("main.index"))
    assert response.status_code == 200
    assert len(captured_templates) == 1
    template, context = captured_templates[0]
    assert template.name == "index.html"
    assert context["title"] == "Home"


def test_user(client, captured_templates, test_with_authenticated_user):
    response = client.get(url_for("main.user", username="test_user"))
    assert response.status_code == 200
    assert len(captured_templates) == 1
    template, context = captured_templates[0]
    assert template.name == "user.html"
    assert context["title"] == "Profile Page"
    assert context["user"] == User.query.filter_by(username="test_user").first()
