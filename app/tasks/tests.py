from datetime import date
from flask_login import current_user
from flask import url_for
from app.models import Task, Worker, Investment
from app.tasks.forms import TaskForm, ProgressForm
from app.main.forms import WarrantyForm


class TestTasks:
    @staticmethod
    def test_get(client, captured_templates, test_with_authenticated_user, add_tasks):
        investment = Investment.query.filter_by(name="Test Invest").first()
        current_user.current_invest_id = investment.id
        task1 = Task.query.filter_by(description="test task 1").first()
        task2 = Task.query.filter_by(description="test task 2").first()
        task3 = Task.query.filter_by(description="test task 3").first()
        response = client.get(url_for("tasks.tasks"))
        assert response.status_code == 200
        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "tasks/tasks.html"
        assert context["title"] == "Tasks"
        assert context["tasks_in_progress"] == [task1, task2]
        assert context["realized_tasks"] == [task3]
        assert context["admin"]
        assert context["next_page"] == url_for("tasks.tasks")


class MyTasks:
    @staticmethod
    def test_get(client, captured_templates, test_with_authenticated_user, add_tasks):
        investment = Investment.query.filter_by(name="Test Invest").first()
        current_user.current_invest_id = investment.id
        task2 = Task.query.filter_by(description="test task 2").first()
        task3 = Task.query.filter_by(description="test task 3").first()
        response = client.get(url_for("tasks.my_tasks"))
        assert response.status_code == 200
        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "tasks/tasks.html"
        assert context["title"] == "My Tasks"
        assert context["tasks_in_progress"] == [task2]
        assert context["realized_tasks"] == [task3]
        assert context["admin"]
        assert context["next_page"] == url_for("tasks.my_tasks")


class DeputedTasks:
    @staticmethod
    def test_get(client, captured_templates, test_with_authenticated_user, add_tasks):
        investment = Investment.query.filter_by(name="Test Invest").first()
        current_user.current_invest_id = investment.id
        task1 = Task.query.filter_by(description="test task 1").first()
        task2 = Task.query.filter_by(description="test task 2").first()
        task3 = Task.query.filter_by(description="test task 3").first()
        response = client.get(url_for("tasks.deputed_tasks"))
        assert response.status_code == 200
        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "tasks/tasks.html"
        assert context["title"] == "Deputed Tasks"
        assert context["tasks_in_progress"] == [task1, task2]
        assert context["realized_tasks"] == [task3]
        assert context["admin"]
        assert context["next_page"] == url_for("tasks.deputed_tasks")


class TestAddTask:
    @staticmethod
    def test_get(
        client, captured_templates, test_with_authenticated_user, add_investment
    ):
        investment = Investment.query.filter_by(name="Test Invest").first()
        current_user.current_invest_id = investment.id
        response = client.get(url_for("tasks.add_task"))
        assert response.status_code == 200
        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "tasks/form.html"
        assert context["title"] == "Add Task"
        assert isinstance(context["form"], TaskForm)

    @staticmethod
    def test_post_when_ok(
        client, captured_templates, test_with_authenticated_user, add_investment
    ):
        investment = Investment.query.filter_by(name="Test Invest").first()
        current_user.current_invest_id = investment.id
        form = TaskForm(
            description="test task",
            deadline=date(year=2021, month=1, day=12),
            priority=5,
            executor_name="unlogged_user",
        )
        response = client.post(
            url_for("tasks.add_task"), data=form.data, follow_redirects=True
        )
        assert response.status_code == 200
        assert b"You have created the task successfully." in response.data
        assert Task.query.filter_by(description="test task").first()

    @staticmethod
    def test_post_when_no_orderer(
        client, captured_templates, test_with_authenticated_user, add_investment
    ):
        form = TaskForm(
            description="test task",
            deadline=date(year=2021, month=1, day=12),
            executor_name="unlogged_user",
        )
        response = client.post(
            url_for("tasks.add_task"), data=form.data, follow_redirects=True
        )
        assert response.status_code == 200
        assert b"Choose investment first." in response.data
        assert not Task.query.filter_by(description="test task").first()

    @staticmethod
    def test_post_when_no_executor(
        client, captured_templates, test_with_authenticated_user, add_investment
    ):
        investment = Investment.query.filter_by(name="Test Invest").first()
        current_user.current_invest_id = investment.id
        form = TaskForm(
            description="test task",
            deadline=date(year=2021, month=1, day=12),
            executor_name="wrong_username",
        )
        response = client.post(
            url_for("tasks.add_task"), data=form.data, follow_redirects=True
        )
        assert response.status_code == 200
        assert (
            b"We can not find worker with this name. Check typing and try again."
            in response.data
        )
        assert not Task.query.filter_by(description="test task").first()


class TestEditTask:
    @staticmethod
    def test_get(client, captured_templates, test_with_authenticated_user, add_tasks):
        investment = Investment.query.filter_by(name="Test Invest").first()
        current_user.current_invest_id = investment.id
        task = Task.query.filter_by(description="test task 1").first()
        response = client.get(url_for("tasks.edit_task", _id=task.id))
        assert response.status_code == 200
        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "tasks/form.html"
        assert context["title"] == "Edit Task"
        assert isinstance(context["form"], TaskForm)
        assert context["form"].description.data == task.description
        assert context["form"].deadline.data == task.deadline
        assert context["form"].priority.data == task.priority
        assert context["form"].executor_name.data == task.executor.users.username

    @staticmethod
    def test_post_when_ok(
        client, captured_templates, test_with_authenticated_user, add_tasks
    ):
        investment = Investment.query.filter_by(name="Test Invest").first()
        current_user.current_invest_id = investment.id
        task = Task.query.filter_by(description="test task 1").first()
        form = TaskForm(
            description="new task name",
            deadline=date(year=2021, month=1, day=15),
            priority=3,
            executor_name="active_user",
        )
        response = client.post(
            url_for("tasks.edit_task", _id=task.id),
            data=form.data,
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"You have edited the task successfully." in response.data
        assert task.description == "new task name"
        assert task.deadline == date(year=2021, month=1, day=15)
        assert task.priority == 3
        assert task.executor.users.username == "active_user"


class TestDeleteTask:
    @staticmethod
    def test_get(client, captured_templates, test_with_authenticated_user, add_tasks):
        task = Task.query.filter_by(description="test task 1").first()
        response = client.get(url_for("tasks.delete_task", _id=task.id))
        assert response.status_code == 200
        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "warranty_form.html"
        assert context["title"] == "Delete Task"
        assert isinstance(context["form"], WarrantyForm)

    @staticmethod
    def test_post_when_no_chosen(client, test_with_authenticated_user, add_tasks):
        task = Task.query.filter_by(description="test task 1").first()
        response = client.post(
            url_for("tasks.delete_task", _id=task.id),
            data={"no": True},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"The task has not been deleted." in response.data
        assert Task.query.filter_by(description="test task 1").first()

    @staticmethod
    def test_post_when_no_task_id_given(client, test_with_authenticated_user):
        response = client.post(
            url_for("tasks.delete_task"), data={"yes": True}, follow_redirects=True
        )
        assert response.status_code == 200
        assert b"You have deleted the task successfully." in response.data

    @staticmethod
    def test_post_when_ok(client, test_with_authenticated_user, add_tasks):
        task = Task.query.filter_by(description="test task 1").first()
        response = client.post(
            url_for("tasks.delete_task", _id=task.id),
            data={"yes": True},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"You have deleted the task successfully." in response.data
        assert not Task.query.filter_by(description="test task 1").first()


class TestChangeProgress:
    @staticmethod
    def test_get(client, captured_templates, test_with_authenticated_user, add_tasks):
        task = Task.query.filter_by(description="test task 1").first()
        response = client.get(url_for("tasks.change_progress", _id=task.id))
        assert response.status_code == 200
        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "tasks/form.html"
        assert context["title"] == "Change Progress"
        assert isinstance(context["form"], ProgressForm)
        assert context["form"].progress.data == task.progress

    @staticmethod
    def test_post(client, test_with_authenticated_user, add_tasks):
        task = Task.query.filter_by(description="test task 1").first()
        form = ProgressForm(progress=75)
        response = client.post(
            url_for("tasks.change_progress", _id=task.id),
            data=form.data,
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"You have changed the progress successfully." in response.data
        assert task.progress == 75
