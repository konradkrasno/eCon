from flask import url_for
from app.models import User


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
