from flask import url_for

from app.main.populate_db import get_or_create_user
from app.models import User
from app.app_tasks.tasks import delete_if_unused


class TestIndex:
    @staticmethod
    def test_get(client, captured_templates, test_with_authenticated_user):
        response = client.get(url_for("main.index"))
        assert response.status_code == 200
        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "index.html"
        assert context["title"] == "Home"


class TestUser:
    @staticmethod
    def test_get(client, captured_templates, test_with_authenticated_user):
        response = client.get(url_for("main.user", username="test_user"))
        assert response.status_code == 200
        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "user.html"
        assert context["title"] == "Profile Page"
        assert context["user"] == User.query.filter_by(username="test_user").first()


class TestUploadFiles:
    @staticmethod
    def test_get(client, captured_templates, test_with_authenticated_user):
        pass

    @staticmethod
    def test_post(client, test_with_authenticated_user):
        pass


class TestPopulateDB:
    @staticmethod
    def test_get_or_create_user(app_and_db, mocker):
        mocker.patch("app.app_tasks.tasks.delete_if_unused.apply_async")
        assert get_or_create_user("test_user", guest=True)
        delete_if_unused.apply_async.assert_called_once_with(args=("test_user",), countdown=600)
