from flask import url_for

from app.production.custom_registry.forms import CreateTableForm, AddColumnForm
from app.production.custom_registry.registry import Registry


class TestStart:
    @staticmethod
    def test_get():
        pass


class TestCreateTable:
    @staticmethod
    def test_get(client):
        response = client.get(url_for("custom_registry.create_table"))
        assert response.status_code == 200

    @staticmethod
    def test_post(client):
        form = CreateTableForm(
            invest_id=1,
            username="test_user",
            table_name="Test Table",
        )
        response = client.post(
            url_for("custom_registry.create_table"),
            data=form.data,
            follow_redirects=True,
        )
        assert response.status_code == 200


class TestAddColumn:
    @staticmethod
    def test_get():
        pass

    @staticmethod
    def test_post(client):
        form = AddColumnForm(
            invest_id=1,
            username="test_user",
            registry_name="Test Registry",
            name="column 1",
            data_type="string",
        )
        response = client.post(
            url_for("custom_registry.add_column"), data=form.data, follow_redirects=True
        )
        assert response.status_code == 200


class TestRegistry:
    @staticmethod
    def test_create(test_mongo):
        registry = Registry(1, "test_user", "test_registry")
        registry.add_item({"test_field": "test_data"})
        assert test_mongo.investments.find_one(
            {
                "invest_id": 1,
                "registry_name": "investment_1_test_registry",
                "users": {"$in": ["test_user"]},
            }
        )
        assert test_mongo.investment_1_test_registry.find_one(
            {"test_field": "test_data"}
        )

    @staticmethod
    def test_get_registry(add_registries):
        pass

    @staticmethod
    def test_add_registry_to_investments():
        pass

    @staticmethod
    def test_get_user_registries():
        pass
