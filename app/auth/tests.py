from flask import url_for
from flask_login import current_user
from app.auth.forms import (
    LoginForm,
    RegisterForm,
    EditProfileForm,
    ChangePasswordForm,
    ResetPasswordForm,
    CompleteRegistrationForm,
)
from app.main.forms import WarrantyForm
from app.auth.token import get_confirmation_token, verify_token
from app.models import User, Investment, Worker
from app.auth import email


def test_token():
    token = get_confirmation_token(_id=1, text="test_text")
    token = verify_token(token)
    _id = token.get("_id", None)
    text = token.get("text", None)
    assert _id == 1
    assert text == "test_text"

    token = get_confirmation_token(_id=5)
    token = verify_token(token)
    _id = token.get("_id", None)
    assert _id == 5

    token = verify_token(b"wrong_token")
    _id = token.get("_id", None)
    assert not _id

    token = verify_token(b"wrong_token")
    _id = token.get("_id", None)
    text = token.get("text", None)
    assert not _id
    assert not text


class TestLogin:
    @staticmethod
    def test_get(client, captured_templates):
        response = client.get(url_for("auth.login"))
        assert response.status_code == 200
        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "auth/form.html"
        assert context["title"] == "Log In"
        assert isinstance(context["form"], LoginForm)

    @staticmethod
    def test_post_when_valid_data(client, unlogged_user):
        form = LoginForm(username="unlogged_user", password="password")
        response = client.post(
            url_for("auth.login"),
            data=form.data,
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert current_user.username == "unlogged_user"

    @staticmethod
    def test_post_when_wrong_data(client, unlogged_user):
        form = LoginForm(username="unlogged_user", password="wrong_password")
        response = client.post(
            url_for("auth.login"),
            data=form.data,
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Invalid username or password" in response.data

    @staticmethod
    def test_post_when_user_not_active(client, inactive_user):
        form = LoginForm(username="inactive_user", password="password")
        response = client.post(
            url_for("auth.login"),
            data=form.data,
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Check your email to activate your account." in response.data


class TestRegister:
    @staticmethod
    def test_get(client, captured_templates):
        response = client.get(url_for("auth.register"))
        assert response.status_code == 200
        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "auth/form.html"
        assert context["title"] == "Register"
        assert isinstance(context["form"], RegisterForm)

    @staticmethod
    def test_post(client, mocker):
        mocker.patch("app.auth.email.send_register_confirmation")
        form = RegisterForm(
            username="new_test_user",
            email="new_test_user@email.com",
            password="password",
            password2="password",
        )
        response = client.post(
            url_for("auth.register"),
            data=form.data,
            follow_redirects=True,
        )
        assert response.status_code == 200
        user = User.query.filter_by(username=form.username.data).first()
        assert user.username == "new_test_user"
        email.send_register_confirmation.assert_called_once_with(user)
        assert b"Check your email to activate your account." in response.data


class TestActivateAccount:
    @staticmethod
    def test_post_with_valid_token(client, inactive_user):
        token = get_confirmation_token(id=1)
        response = client.post(
            url_for("auth.activate_account", token=token), follow_redirects=True
        )
        assert response.status_code == 200
        user = User.query.get(1)
        assert user.is_active
        assert b"You have activated your account successfully." in response.data

    @staticmethod
    def test_post_with_invalid_token(client, inactive_user):
        token = get_confirmation_token(id=2)
        response = client.post(
            url_for("auth.activate_account", token=token), follow_redirects=True
        )
        assert response.status_code == 200
        user = User.query.get(1)
        assert not user.is_active
        assert b"The activation link is invalid." in response.data


class TestEditProfile:
    @staticmethod
    def test_get(client, captured_templates, test_with_authenticated_user):
        response = client.get(url_for("auth.edit_profile"))
        assert response.status_code == 200
        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "auth/form.html"
        assert context["title"] == "Edit Profile"
        assert isinstance(context["form"], EditProfileForm)

    @staticmethod
    def test_post(client, mocker, test_with_authenticated_user):
        mocker.patch("app.auth.email.send_change_email_confirmation")
        form = EditProfileForm(
            original_username=current_user.username,
            original_email=current_user.email,
            username="new_username",
            email="new_email@email.com",
        )
        response = client.post(
            url_for("auth.edit_profile"), data=form.data, follow_redirects=True
        )
        assert response.status_code == 200
        user = User.query.filter_by(username=form.username.data).first()
        assert user.username == "new_username"
        assert user.email == current_user.email
        email.send_change_email_confirmation.assert_called_once_with(
            form.email.data, user
        )
        assert b"Check your email to confirm the email address change." in response.data
        assert b"You change your profile data." in response.data


class TestActivateEmail:
    @staticmethod
    def test_post_with_valid_email(client, test_with_authenticated_user):
        form = EditProfileForm(
            original_username=current_user.username,
            original_email=current_user.email,
            username="new_username",
            email="new_email@email.com",
        )
        client.post(url_for("auth.edit_profile"), data=form.data, follow_redirects=True)

        token = get_confirmation_token(id=1, email=form.email.data)
        response = client.post(
            url_for("auth.activate_email", token=token), follow_redirects=True
        )
        assert response.status_code == 200
        user = User.query.get(1)
        assert user.email == form.email.data
        assert b"You confirm your new email address." in response.data

    @staticmethod
    def test_post_with_invalid_email(app_and_db, client, test_with_authenticated_user):
        new_email = "second_email@email.com"

        db = app_and_db[1]
        db.session.add(
            User(username="second_user", email=new_email, password="password")
        )
        db.session.commit()

        form = EditProfileForm(
            original_username=current_user.username,
            original_email=current_user.email,
            username="new_username",
            email=new_email,
        )
        client.post(url_for("auth.edit_profile"), data=form.data, follow_redirects=True)

        user = User.query.filter_by(username="active_user").first()
        token = get_confirmation_token(id=user.id, email=form.email.data)
        response = client.post(
            url_for("auth.activate_email", token=token), follow_redirects=True
        )
        assert response.status_code == 200
        user = User.query.get(user.id)
        assert user.email != new_email
        assert b"You can not set this email address." in response.data


class TestChangePassword:
    @staticmethod
    def test_get(client, captured_templates, test_with_authenticated_user):
        response = client.get(url_for("auth.change_password"))
        assert response.status_code == 200
        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "auth/form.html"
        assert context["title"] == "Change Password"
        assert isinstance(context["form"], ChangePasswordForm)

    @staticmethod
    def test_post(client, test_with_authenticated_user):
        form = ChangePasswordForm(password="new_password", password2="new_password")
        response = client.post(
            url_for("auth.change_password"), data=form.data, follow_redirects=True
        )
        assert response.status_code == 200
        assert b"You change your password successfully." in response.data
        user = User.query.get(1)
        assert user.validate_password("new_password")


class TestResetPasswordRequest:
    @staticmethod
    def test_get(client, captured_templates):
        response = client.get(url_for("auth.reset_password_request"))
        assert response.status_code == 200
        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "auth/form.html"
        assert context["title"] == "Reset Password"
        assert isinstance(context["form"], ResetPasswordForm)

    @staticmethod
    def test_post_with_right_email(client, mocker, unlogged_user):
        mocker.patch("app.auth.email.send_password_reset_confirmation")
        form = ResetPasswordForm(email="unlogged_user@email.com")
        response = client.post(
            url_for("auth.reset_password_request"),
            data=form.data,
            follow_redirects=True,
        )
        assert response.status_code == 200
        user = User.query.filter_by(username="unlogged_user").first()
        email.send_password_reset_confirmation.assert_called_once_with(user)
        assert b"Check your email to reset your password." in response.data

    @staticmethod
    def test_post_with_wrong_email(client, mocker, unlogged_user):
        mocker.patch("app.auth.email.send_password_reset_confirmation")
        form = ResetPasswordForm(email="wrong@email.com")
        response = client.post(
            url_for("auth.reset_password_request"),
            data=form.data,
            follow_redirects=True,
        )
        assert response.status_code == 200
        email.send_password_reset_confirmation.assert_not_called()
        assert b"Check your email to reset your password." in response.data


class TestResetPassword:
    @staticmethod
    def test_get(client, captured_templates, unlogged_user):
        user = User.query.filter_by(username="unlogged_user").first()
        token = get_confirmation_token(id=user.id)
        response = client.get(url_for("auth.reset_password", token=token))
        assert response.status_code == 200
        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "auth/form.html"
        assert context["title"] == "Change Password"
        assert isinstance(context["form"], ChangePasswordForm)

    @staticmethod
    def test_post_with_valid_token(client, unlogged_user):
        user = User.query.filter_by(username="unlogged_user").first()
        token = get_confirmation_token(id=user.id)
        form = ChangePasswordForm(password="new_password", password2="new_password")
        response = client.post(
            url_for("auth.reset_password", token=token),
            data=form.data,
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Your password has been reset." in response.data
        assert user.validate_password("new_password")

    @staticmethod
    def test_post_with_invalid_token(client, unlogged_user):
        user = User.query.filter_by(username="unlogged_user").first()
        form = ChangePasswordForm(password="new_password", password2="new_password")
        response = client.post(
            url_for("auth.reset_password", token="invalid_token"),
            data=form.data,
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert not b"Your password has been reset." in response.data
        assert not user.validate_password("new_password")


class TestCompleteRegistration:
    @staticmethod
    def test_get(client, captured_templates, inactive_user):
        user = User.query.filter_by(username="inactive_user").first()
        token = get_confirmation_token(id=user.id)
        response = client.get(url_for("auth.complete_registration", token=token))
        assert response.status_code == 200
        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "auth/form.html"
        assert context["title"] == "Complete Registration"
        assert isinstance(context["form"], CompleteRegistrationForm)

    @staticmethod
    def test_post_with_valid_token(client, inactive_user):
        user = User.query.filter_by(username="inactive_user").first()
        token = get_confirmation_token(id=user.id)
        form = CompleteRegistrationForm(
            username="new_test_user", password="new_password", password2="new_password"
        )
        response = client.post(
            url_for("auth.complete_registration", token=token),
            data=form.data,
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"You have successfully complete the registration." in response.data
        assert user.username == "new_test_user"
        assert user.validate_password("new_password")
        assert user.is_active

    @staticmethod
    def test_post_with_invalid_token(client, inactive_user):
        user = User.query.filter_by(username="inactive_user").first()
        form = CompleteRegistrationForm(
            username="new_test_user", password="new_password", password2="new_password"
        )
        response = client.post(
            url_for("auth.complete_registration", token="wrong_token"),
            data=form.data,
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert not b"You have successfully complete the registration." in response.data
        assert not user.username == "new_test_user"
        assert not user.validate_password("new_password")
        assert not user.is_active


class TestDeleteAccount:
    @staticmethod
    def test_get(client, captured_templates, test_with_authenticated_user):
        response = client.get(url_for("auth.delete_account", username="active_user"))
        assert response.status_code == 200
        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "warranty_form.html"
        assert context["title"] == "Delete Account"
        assert isinstance(context["form"], WarrantyForm)

    @staticmethod
    def test_post_when_no(client, test_with_authenticated_user):
        response = client.post(
            url_for("auth.delete_account", username="active_user"),
            data={"no": True},
            follow_redirects=True,
        )
        assert response.status_code == 200

    @staticmethod
    def test_post_when_user_is_lonely_admin(
        app_and_db, client, test_with_authenticated_user, inactive_user
    ):
        db = app_and_db[1]
        investment = Investment(name="Test Invest")
        user1 = User.query.filter_by(username="active_user").first()
        user2 = User.query.filter_by(username="inactive_user").first()
        worker1 = Worker(position="pos1", admin=True, user_id=user1.id)
        worker2 = Worker(position="pos2", admin=False, user_id=user2.id)
        investment.workers.append(worker1)
        investment.workers.append(worker2)
        db.session.add(investment)
        db.session.commit()

        response = client.post(
            url_for("auth.delete_account", username="active_user"),
            data={"yes": True},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert User.query.filter_by(username="active_user").first()
        assert len(Worker.query.all()) == 2
        assert (
            b"This accounts is only admin in projects: [&#39;Test Invest&#39;]."
            b" Give root permission to other user and try again" in response.data
        )

    @staticmethod
    def test_post_when_delete(
        app_and_db, client, test_with_authenticated_user, inactive_user
    ):
        db = app_and_db[1]

        investment1 = Investment(name="Test Invest 1")
        user1 = User.query.filter_by(username="active_user").first()
        user2 = User.query.filter_by(username="inactive_user").first()
        worker1 = Worker(position="pos1", admin=True, user_id=user1.id)
        worker2 = Worker(position="pos2", admin=True, user_id=user2.id)
        investment1.workers.append(worker1)
        investment1.workers.append(worker2)

        investment2 = Investment(name="Test Invest 2")
        worker = Worker(position="pos1", admin=True, user_id=user1.id)
        investment2.workers.append(worker)

        db.session.add(investment1)
        db.session.add(investment2)
        db.session.commit()

        response = client.post(
            url_for("auth.delete_account", username="active_user"),
            data={"yes": True},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert not User.query.filter_by(username="active_user").first()
        assert Worker.query.all() == Worker.query.filter_by(user_id=user2.id).all()
        assert (
            Investment.query.all()
            == Investment.query.filter_by(name="Test Invest 1").all()
        )
        assert b"The account has been deleted." in response.data
