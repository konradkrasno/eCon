from flask import url_for
from flask_login import current_user

from app.auth import email
from app.main.forms import WarrantyForm
from app.models import User, Investment, Worker
from app.team.forms import CreateWorkerForm, EditWorkerForm


class TestTeam:
    @staticmethod
    def test_get(
        client, captured_templates, test_with_authenticated_user, add_investment
    ):
        investment = Investment.query.filter_by(name="Test Invest").first()
        current_user.current_invest_id = investment.id
        worker1 = Worker.query.filter_by(position="admin").first()
        worker2 = Worker.query.filter_by(position="second worker").first()
        response = client.get(url_for("team.team"))
        assert response.status_code == 200
        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "team/team.html"
        assert context["title"] == "Team"
        assert context["team"] == [worker1, worker2]
        assert context["admin"]


class TestAddWorker:
    @staticmethod
    def test_get_with_no_admin(client, test_with_authenticated_user, add_investment):
        worker = Worker.query.filter_by(user_id=current_user.id).first()
        worker.admin = False
        investment = Investment.query.filter_by(name="Test Invest").first()
        current_user.current_invest_id = investment.id
        response = client.get(url_for("team.add_worker"))
        assert response.status_code == 302

    @staticmethod
    def test_get_with_admin(
        client, captured_templates, test_with_authenticated_user, add_investment
    ):
        investment = Investment.query.filter_by(name="Test Invest").first()
        current_user.current_invest_id = investment.id
        response = client.get(url_for("team.add_worker"))
        assert response.status_code == 200
        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "team/form.html"
        assert context["title"] == "Add Worker"
        assert isinstance(context["form"], CreateWorkerForm)

    @staticmethod
    def test_post(client, mocker, test_with_authenticated_user, add_investment):
        mocker.patch("app.auth.email.send_complete_registration_mail")
        investment = Investment.query.filter_by(name="Test Invest").first()
        current_user.current_invest_id = investment.id
        form = CreateWorkerForm(
            email="new_worker@email.com", position="new position", admin=False
        )
        response = client.post(
            url_for("team.add_worker"), data=form.data, follow_redirects=True
        )
        assert response.status_code == 200
        new_user = User.query.filter_by(username=form.email.data).first()
        assert new_user
        assert Worker.query.filter_by(user_id=new_user.id).first()
        email.send_complete_registration_mail.assert_called_once_with(new_user)
        assert b"You have added new worker successfully." in response.data

    @staticmethod
    def test_post_when_worker_duplicated(
        client, mocker, test_with_authenticated_user, add_investment
    ):
        mocker.patch("app.auth.email.send_complete_registration_mail")
        investment = Investment.query.filter_by(name="Test Invest").first()
        current_user.current_invest_id = investment.id
        form = CreateWorkerForm(
            email="active_user@email.com", position="new position", admin=False
        )
        response = client.post(
            url_for("team.add_worker"), data=form.data, follow_redirects=True
        )
        assert response.status_code == 200
        assert b"This user is already added to workers." in response.data
        new_user = User.query.filter_by(username=form.email.data).first()
        assert not new_user
        assert not Worker.query.filter_by(position="new position").first()
        email.send_complete_registration_mail.assert_not_called()


class TestEditWorker:
    @staticmethod
    def test_get_with_no_admin(client, test_with_authenticated_user, add_investment):
        worker = Worker.query.filter_by(user_id=current_user.id).first()
        worker.admin = False
        investment = Investment.query.filter_by(name="Test Invest").first()
        current_user.current_invest_id = investment.id
        response = client.get(
            url_for("team.edit_worker", _id=investment.workers.first().id)
        )
        assert response.status_code == 302

    @staticmethod
    def test_get_with_admin(
        client, captured_templates, test_with_authenticated_user, add_investment
    ):
        investment = Investment.query.filter_by(name="Test Invest").first()
        current_user.current_invest_id = investment.id
        response = client.get(
            url_for("team.edit_worker", _id=investment.workers.first().id)
        )
        assert response.status_code == 200
        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "team/form.html"
        assert context["title"] == "Edit Worker"
        assert isinstance(context["form"], EditWorkerForm)
        assert context["form"].position.data == "admin"

    @staticmethod
    def test_post(client, test_with_authenticated_user, add_investment):
        investment = Investment.query.filter_by(name="Test Invest").first()
        current_user.current_invest_id = investment.id
        form = EditWorkerForm(position="new position")
        worker = investment.workers.first()
        response = client.post(
            url_for("team.edit_worker", _id=worker.id),
            data=form.data,
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert (
            b"You have edited the information about the worker successfully."
            in response.data
        )
        assert worker.position == "new position"


class TestDeleteWorker:
    @staticmethod
    def test_get_with_no_admin(client, test_with_authenticated_user, add_investment):
        worker = Worker.query.filter_by(user_id=current_user.id).first()
        worker.admin = False
        investment = Investment.query.filter_by(name="Test Invest").first()
        current_user.current_invest_id = investment.id
        response = client.get(
            url_for("team.delete_worker", _id=investment.workers.first().id)
        )
        assert response.status_code == 302

    @staticmethod
    def test_get_with_admin(
        client, captured_templates, test_with_authenticated_user, add_investment
    ):
        investment = Investment.query.filter_by(name="Test Invest").first()
        current_user.current_invest_id = investment.id
        response = client.get(
            url_for("team.delete_worker", _id=investment.workers.first().id)
        )
        assert response.status_code == 200
        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "warranty_form.html"
        assert context["title"] == "Delete Worker"
        assert isinstance(context["form"], WarrantyForm)

    @staticmethod
    def test_post(client, test_with_authenticated_user, add_investment):
        investment = Investment.query.filter_by(name="Test Invest").first()
        current_user.current_invest_id = investment.id
        worker = Worker.query.filter_by(position="second worker").first()
        response = client.post(
            url_for("team.delete_worker", _id=worker.id),
            data={"yes": True},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"You have been deleted worker successfully." in response.data
        assert not Worker.query.filter_by(position="second worker").first()

    @staticmethod
    def test_post_when_delete_yourself(
        client, test_with_authenticated_user, add_investment
    ):
        investment = Investment.query.filter_by(name="Test Invest").first()
        current_user.current_invest_id = investment.id
        worker = Worker.query.filter_by(position="admin").first()
        response = client.post(
            url_for("team.delete_worker", _id=worker.id),
            data={"yes": True},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"You can not delete yourself!" in response.data
        assert Worker.query.filter_by(position="admin").first()


class TestChangeRootPermission:
    @staticmethod
    def test_get_with_no_admin(client, test_with_authenticated_user, add_investment):
        worker = Worker.query.filter_by(user_id=current_user.id).first()
        worker.admin = False
        investment = Investment.query.filter_by(name="Test Invest").first()
        current_user.current_invest_id = investment.id
        response = client.get(
            url_for("team.change_root_permission", _id=investment.workers.first().id)
        )
        assert response.status_code == 302

    @staticmethod
    def test_get_when_deleting_last_admin(
        client, test_with_authenticated_user, add_investment
    ):
        investment = Investment.query.filter_by(name="Test Invest").first()
        current_user.current_invest_id = investment.id
        worker = Worker.query.filter_by(position="admin").first()
        response = client.get(
            url_for("team.change_root_permission", _id=worker.id),
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"You can not delete last admin!" in response.data

    @staticmethod
    def test_get_when_possible_to_change(
        client, captured_templates, test_with_authenticated_user, add_investment
    ):
        investment = Investment.query.filter_by(name="Test Invest").first()
        current_user.current_invest_id = investment.id
        worker = Worker.query.filter_by(position="second worker").first()
        response = client.get(
            url_for("team.change_root_permission", _id=worker.id),
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "warranty_form.html"
        assert context["title"] == "Change Root Permission"
        assert isinstance(context["form"], WarrantyForm)

    @staticmethod
    def test_post(client, test_with_authenticated_user, add_investment):
        investment = Investment.query.filter_by(name="Test Invest").first()
        current_user.current_invest_id = investment.id
        # Giving root permission
        worker = Worker.query.filter_by(position="second worker").first()
        assert not worker.admin
        response = client.post(
            url_for("team.change_root_permission", _id=worker.id),
            data={"yes": True},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert (
            b"You have changed worker&#39;s root permission successfully."
            in response.data
        )
        assert worker.admin
        # Taking away root permission
        worker = Worker.query.filter_by(position="admin").first()
        assert worker.admin
        response = client.post(
            url_for("team.change_root_permission", _id=worker.id),
            data={"yes": True},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert (
            b"You have changed worker&#39;s root permission successfully."
            in response.data
        )
        assert not worker.admin
