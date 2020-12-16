import pytest

from app.main.forms import LoginForm
from app.tests.conftest import assert_flashes


def test_index(client, captured_templates):
    response = client.get("/")
    assert response.status_code == 200
    assert len(captured_templates) == 1
    template, context = captured_templates[0]
    assert template.name == "index.html"
    assert context["title"] == "Home"
    assert context["user"] == {"username": "Konrad"}


def test_login(client, captured_templates):
    response = client.get("/login")
    assert response.status_code == 200
    assert len(captured_templates) == 1
    template, context = captured_templates[0]
    assert template.name == "login.html"
    assert context["title"] == "Sign In"
    assert isinstance(context["form"], LoginForm)


@pytest.mark.parametrize(
    "username, password, message",
    [
        ("Konrad", "", b"[This field is required.]"),
        ("", "test_password", b"[This field is required.]"),
    ],
)
def test_login_validate_input(client, username, password, message):
    response = client.post("/login", data={"username": username, "password": password})
    assert message in response.data


# def test_login_when_login(client):
#     client.post("/login", data={"username": "Konrad", "password": "test_password"})
#     assert_flashes(client, "Konrad, you are logged in.")
