from flask import url_for
from flask_login import current_user

from app.investments.forms import InvestmentForm
from app.main.forms import WarrantyForm
from app.models import User, Investment, Worker


class TestInvestList:
    @staticmethod
    def test_get(client, captured_templates, mocker, test_with_authenticated_user):
        mocker.patch("app.models.Investment.get_by_user_id")
        user = User.query.filter_by(username="active_user").first()
        response = client.get(url_for("investments.invest_list"))
        assert response.status_code == 200
        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "investments/investments.html"
        assert context["title"] == "Investments"
        assert context["username"] == user.username
        assert context["investments"]
        Investment.get_by_user_id.assert_called_once_with(user.id)


class TestCreate:
    @staticmethod
    def test_get(client, captured_templates, test_with_authenticated_user):
        response = client.get(url_for("investments.create"))
        assert response.status_code == 200
        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "investments/form.html"
        assert context["title"] == "Create Investment"
        assert isinstance(context["form"], InvestmentForm)

    @staticmethod
    def test_post(client, test_with_authenticated_user):
        user = User.query.filter_by(username="active_user").first()
        form = InvestmentForm(name="New Invest", description="test text")
        response = client.post(
            url_for("investments.create"), data=form.data, follow_redirects=True
        )
        assert response.status_code == 200
        assert b"You have created new investment successfully." in response.data
        investment = Investment.query.filter_by(name="New Invest").first()
        workers = Worker.get_team(investment.id)
        assert investment.description == "test text"
        assert investment.workers.all() == workers
        assert workers[0].user_id == user.id


class TestInfo:
    @staticmethod
    def test_get(
        client, captured_templates, test_with_authenticated_user, add_investment
    ):
        investment = Investment.query.filter_by(name="Test Invest").first()
        response = client.get(url_for("investments.info", _id=investment.id))
        assert response.status_code == 200
        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "investments/info.html"
        assert context["title"] == "Investment"
        assert context["investment"] == investment
        assert context["admin"]


class TestChoose:
    @staticmethod
    def test_post(client, test_with_authenticated_user):
        response = client.get(
            url_for("investments.choose", _id=100), follow_redirects=True
        )
        assert response.status_code == 200
        assert current_user.current_invest_id == 100


class TestEdit:
    @staticmethod
    def test_get_with_no_investment(client, test_with_authenticated_user):
        response = client.get(url_for("investments.edit", _id=100))
        assert response.status_code == 302

    @staticmethod
    def test_get_with_no_admin(client, test_with_authenticated_user, add_investment):
        worker = Worker.query.filter_by(user_id=current_user.id).first()
        worker.admin = False
        investment = Investment.query.filter_by(name="Test Invest").first()
        response = client.get(url_for("investments.edit", _id=investment.id))
        assert response.status_code == 302

    @staticmethod
    def test_get_with_admin(
        client, captured_templates, test_with_authenticated_user, add_investment
    ):
        investment = Investment.query.filter_by(name="Test Invest").first()
        response = client.get(url_for("investments.edit", _id=investment.id))
        assert response.status_code == 200
        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "investments/form.html"
        assert context["title"] == "Edit Investment"
        assert isinstance(context["form"], InvestmentForm)
        assert context["form"].name.data == "Test Invest"
        assert context["form"].description.data == "test text"

    @staticmethod
    def test_post(client, test_with_authenticated_user, add_investment):
        investment = Investment.query.filter_by(name="Test Invest").first()
        form = InvestmentForm(
            name="New Invest Name", description="new invest description"
        )
        response = client.post(
            url_for("investments.edit", _id=investment.id),
            data=form.data,
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"You have edited the investment successfully." in response.data
        assert investment.name == "New Invest Name"
        assert investment.description == "new invest description"


class TestDelete:
    @staticmethod
    def test_get_with_no_admin(
        client,
        captured_templates,
        test_with_authenticated_user,
        add_investment,
    ):
        worker = Worker.query.filter_by(user_id=current_user.id).first()
        worker.admin = False
        investment = Investment.query.filter_by(name="Test Invest").first()
        response = client.get(url_for("investments.delete", _id=investment.id))
        assert response.status_code == 302

    @staticmethod
    def test_get_with_admin(
        client, captured_templates, test_with_authenticated_user, add_investment
    ):
        investment = Investment.query.filter_by(name="Test Invest").first()
        response = client.get(url_for("investments.delete", _id=investment.id))
        assert response.status_code == 200
        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "warranty_form.html"
        assert context["title"] == "Delete Investment"
        assert isinstance(context["form"], WarrantyForm)

    @staticmethod
    def test_post(client, test_with_authenticated_user, add_investment):
        investment = Investment.query.filter_by(name="Test Invest").first()
        response = client.post(
            url_for("investments.delete", _id=investment.id),
            data={"yes": True},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Investment has been deleted." in response.data
        assert not Investment.query.filter_by(name="Test Invest").first()
