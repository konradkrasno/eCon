import pytest
import datetime

from app.models import Hole, Processing, Wall, User, Investment, Worker, Task
from app.conftest import contexts_required


class TestMasonryWorks:
    @staticmethod
    def test_create_item_when_wrong_attribute(wall_data):
        wall_data["wrong_attr"] = 5
        item = Wall.create_item(**wall_data)
        assert item

    @staticmethod
    def test_update_item(add_wall):
        wall = Wall.query.first()
        wall = Wall.update_item(wall, object="K", level=5)
        assert wall.object == "K"
        assert wall.level == 5

    @staticmethod
    def test_create_hole(app_and_db):
        app, db = app_and_db
        hole = Hole(width=1.2, height=2, amount=2)
        db.session.add(hole)
        db.session.commit()
        hole = Hole.query.filter_by(width=1.2).first()
        assert hole.width == 1.2
        assert hole.height == 2
        assert hole.amount == 2
        assert hole.area == 2.4
        assert hole.total_area == 4.8
        assert hole.below_3m2

    @staticmethod
    def test_edit_hole(app_and_db):
        app, db = app_and_db
        hole = Hole(width=1.2, height=2, amount=2)
        db.session.add(hole)
        db.session.commit()
        hole = Hole.query.filter_by(width=1.2).first()
        hole.width = 2.5
        assert hole.width == 2.5
        assert hole.height == 2
        assert hole.amount == 2
        assert hole.area == 5.0
        assert hole.total_area == 10.0
        assert not hole.below_3m2

    @staticmethod
    def test_create_processing(app_and_db):
        app, db = app_and_db
        processing = Processing(year=2020, month="December", done=0.4)
        db.session.add(processing)
        db.session.commit()
        processing = Processing.query.filter_by(id=1).first()
        assert processing.done == 0.4

    @staticmethod
    def test_create_processing_with_done_above_1():
        with pytest.raises(ValueError):
            Processing(year=2020, month="December", done=1.2)

    @staticmethod
    def test_edit_processing(app_and_db):
        app, db = app_and_db
        processing = Processing(year=2020, month="December", done=0.4)
        processing.done = 0.6
        db.session.add(processing)
        db.session.commit()
        processing = Processing.query.filter_by(id=1).first()
        assert processing.done == 0.6

    @staticmethod
    def test_edit_processing_with_done_above_1():
        processing = Processing(year=2020, month="December", done=0.4)
        with pytest.raises(ValueError):
            processing.done = 1.2

    @staticmethod
    def test_add_wall(app_and_db, wall_data):
        Wall.add_wall(**wall_data)
        wall = Wall.query.first()
        Wall.add_hole(wall.id, width=1.2, height=2.0, amount=2)
        Wall.add_hole(wall.id, width=2.2, height=2.0, amount=1)
        Wall.add_processing(wall.id, year=2020, month="December", done=0.4)
        assert wall.wall_height == 3.1
        assert wall.gross_wall_area == 32.55
        assert wall.wall_area_to_survey == 23.35
        assert wall.wall_area_to_sale == 29.15
        assert wall.left_to_sale == 0.6

    @staticmethod
    def test_add_hole_without_height(add_wall):
        wall = Wall.query.first()
        Wall.add_hole(wall.id, width=1.2, amount=2)
        hole = Hole.query.first()
        assert hole.height == None
        with pytest.raises(ValueError):
            assert hole.area

    @staticmethod
    def test_add_processing(add_wall):
        wall = Wall.query.first()
        assert wall.left_to_sale == 1.0
        Wall.add_processing(wall.id, year=2020, month="December", done=0.4)
        Wall.add_processing(wall.id, year=2020, month="December", done=0.5)
        assert wall.left_to_sale == 0.1

    @staticmethod
    def test_add_processing_when_overrun(add_wall):
        wall = Wall.query.first()
        Wall.add_processing(wall.id, year=2020, month="December", done=0.4)
        Wall.add_processing(wall.id, year=2020, month="December", done=0.7)
        wall = Wall.query.filter_by(id=wall.id).first()
        assert wall.processing.filter_by(id=1).first().done == 0.4
        assert wall.processing.filter_by(id=2).first().done == 0.6
        assert wall.left_to_sale == 0.0

    @staticmethod
    def test_add_processing_when_done_above_1(add_wall):
        wall = Wall.query.first()
        Wall.add_processing(wall.id, year=2020, month="December", done=2)
        wall = Wall.query.filter_by(id=wall.id).first()
        assert wall.processing[0].done == 1.0
        assert wall.left_to_sale == 0.0

    @staticmethod
    def test_update_item_when_wrong_attr(wall_data):
        wall = Wall.create_item(**wall_data)
        wall = Wall.update_item(wall, wrong_attr1="K", wrong_attr2=5)
        assert wall.sector == "G"
        assert wall.level == 2

    @staticmethod
    def test_update_wall(add_wall):
        wall = Wall.query.first()
        assert wall.wall_height == 3.1
        assert wall.gross_wall_area == 32.55
        assert wall.wall_area_to_survey == 32.55
        assert wall.wall_area_to_sale == 32.55
        assert wall.left_to_sale == 1.0
        Wall.edit_wall(wall.id, floor_ord=4)
        assert wall.wall_height == 2.2
        assert wall.gross_wall_area == 23.1
        assert wall.wall_area_to_survey == 23.1
        assert wall.wall_area_to_sale == 23.1
        assert wall.left_to_sale == 1.0

    @staticmethod
    def test_update_hole(add_wall):
        wall = Wall.query.first()
        Wall.add_hole(wall.id, width=1.2, height=2.0, amount=2)
        assert wall.holes[0].width == 1.2
        assert wall.holes[0].height == 2.0
        assert wall.holes[0].amount == 2
        assert wall.wall_area_to_survey == 27.75
        hole = wall.holes[0]
        Wall.edit_hole(hole.id, width=1.5, height=2.5, amount=1)
        assert wall.holes[0].width == 1.5
        assert wall.holes[0].height == 2.5
        assert wall.holes[0].amount == 1
        assert wall.wall_area_to_survey == 28.8

    @staticmethod
    def test_update_processing(add_wall):
        wall = Wall.query.first()
        Wall.add_processing(wall.id, year=2020, month="December", done=0.3)
        assert wall.processing[0].year == 2020
        assert wall.processing[0].month == "December"
        assert wall.processing[0].done == 0.3
        assert wall.left_to_sale == 0.7
        processing = wall.processing[0]
        Wall.edit_processing(processing.id, year=2021, month="January", done=0.6)
        assert wall.processing[0].year == 2021
        assert wall.processing[0].month == "January"
        assert wall.processing[0].done == 0.6
        assert wall.left_to_sale == 0.4

    @staticmethod
    def test_update_processing_when_overrun(add_wall):
        wall = Wall.query.first()
        Wall.add_processing(wall.id, year=2020, month="December", done=0.6)
        Wall.add_processing(wall.id, year=2020, month="December", done=0.3)
        assert wall.processing.filter_by(id=1).first().done == 0.6
        assert wall.processing.filter_by(id=2).first().done == 0.3
        assert wall.left_to_sale == 0.1
        Wall.edit_processing(2, done=0.5)
        assert wall.processing.filter_by(id=1).first().done == 0.6
        assert wall.processing.filter_by(id=2).first().done == 0.4
        assert wall.left_to_sale == 0.0

    @staticmethod
    def test_update_processing_when_done_above_1(add_wall):
        wall = Wall.query.first()
        Wall.add_processing(wall.id, year=2020, month="December", done=0.6)
        processing = wall.processing[0]
        Wall.edit_processing(processing.id, done=1.35)
        assert wall.processing[0].done == 1.0
        assert wall.left_to_sale == 0.0

    @staticmethod
    def test_delete_wall(add_wall):
        Wall.add_hole(wall_id=1, width=1, height=2, amonunt=1)
        Wall.add_processing(wall_id=1, year=2020, month="December", done=0.5)
        assert Wall.query.filter_by(id=1).first()
        Wall.delete_wall(1)
        assert not Wall.query.filter_by(id=1).first()

    @staticmethod
    def test_delete_wall_when_no_wall(app_and_db):
        assert not Wall.query.filter_by(id=1).first()
        Wall.delete_wall(1)

    @staticmethod
    def test_delete_hole(add_wall):
        Wall.add_hole(wall_id=1, width=1, height=2, amonunt=1)
        assert Hole.query.filter_by(id=1).first()
        Wall.delete_hole(1)
        assert not Hole.query.filter_by(id=1).first()

    @staticmethod
    def test_delete_hole_when_no_hole(app_and_db):
        assert not Hole.query.filter_by(id=1).first()
        Wall.delete_hole(1)

    @staticmethod
    def test_delete_processing(add_wall):
        Wall.add_processing(wall_id=1, year=2020, month="December", done=0.5)
        assert Processing.query.filter_by(id=1).first()
        Wall.delete_processing(1)
        assert not Processing.query.filter_by(id=1).first()

    @staticmethod
    def test_delete_processing_when_no_processing(app_and_db):
        assert not Processing.query.filter_by(id=1).first()
        Wall.delete_processing(1)

    @staticmethod
    @contexts_required
    def test_upload_walls(app_and_db, add_investment):
        investment = Investment.query.first()
        messages = Wall.upload_walls(investment.id, "test/walls.csv")
        assert len(Wall.query.all()) == 5
        assert len(messages) == 2
        assert messages[0] == "Uploaded 6 items."
        assert (
            messages[1]
            == "Items: [8, 9, 10, 11, 12, 13, 14, 15] not added because they has the wrong format."
        )
        assert Wall.query.filter_by(id=1).first().wall_width == 18

    @staticmethod
    @contexts_required
    def test_upload_walls_when_wrong_file(app_and_db, add_investment):
        investment = Investment.query.first()
        messages = Wall.upload_walls(investment.id, "test/holes.csv")
        assert len(Wall.query.all()) == 0
        assert len(messages) == 1
        assert messages[0] == "Uploaded 0 items."

    @staticmethod
    @contexts_required
    def test_upload_holes(app_and_db, add_investment):
        investment = Investment.query.first()
        Wall.upload_walls(investment.id, "test/walls.csv")
        Wall.upload_holes(investment.id, "test/holes.csv")
        messages = Wall.upload_holes(investment.id, "test/holes.csv")
        assert len(Hole.query.all()) == 5
        assert len(messages) == 3
        assert messages[0] == "Uploaded 5 items."
        assert (
            messages[1]
            == "Items: [5, 1, 1, 1] not added because they has the wrong format."
        )
        assert (
            messages[2]
            == "Items: [6, 7, 12, 13, 14, 15, 16, 17] not added because wall with specified id does not exist. Add wall first."
        )

    @staticmethod
    @contexts_required
    def test_upload_processing(app_and_db, add_investment):
        investment = Investment.query.first()
        Wall.upload_walls(investment.id, "test/walls.csv")
        Wall.upload_processing(investment.id, "test/processing.csv")
        messages = Wall.upload_processing(investment.id, "test/processing.csv")
        assert len(Processing.query.all()) == 6
        assert len(messages) == 4
        assert messages[0] == "Uploaded 6 items."
        assert (
            messages[1]
            == "Items: [1, 1, 1, 2, 2] not added because they has the wrong format."
        )
        assert (
            messages[2]
            == "Items: [7, 8, 9] not added because wall with specified id does not exist. Add wall first."
        )
        assert (
            messages[3] == "Items: [1, 3] not added because value of left_to_sale is 0."
        )


class TestWorker:
    @staticmethod
    def test_belongs_to_investment(app_and_db, active_user):
        db = app_and_db[1]
        investment = Investment(name="test invest")
        worker = Worker(position="pos1", user_id=1)
        investment.workers.append(worker)
        db.session.add(investment)
        db.session.commit()

        assert Worker.belongs_to_investment(
            email="active_user@email.com", investment_id=1
        )
        assert not Worker.belongs_to_investment(
            email="another@email.com", investment_id=1
        )

    @staticmethod
    def test_is_admin(app_and_db, active_user):
        db = app_and_db[1]
        db.session.add(Investment(name="test invest 1"))
        db.session.add(Investment(name="test invest 2"))
        db.session.add(Worker(position="pos1", admin=True, user_id=1, investment_id=1))
        db.session.add(Worker(position="pos2", admin=False, user_id=1, investment_id=2))
        db.session.commit()

        assert Worker.is_admin(user_id=1, investment_id=1)
        assert not Worker.is_admin(user_id=1, investment_id=2)

    @staticmethod
    def test_get_team(app_and_db, active_user):
        db = app_and_db[1]
        db.session.add(Investment(name="test invest 1"))
        db.session.add(Worker(position="pos1", admin=True, investment_id=1))
        db.session.add(Worker(position="pos2", admin=False, investment_id=1))
        db.session.add(Worker(position="pos2", admin=False, investment_id=1))
        db.session.add(Investment(name="test invest 2"))
        db.session.add(Worker(position="pos2", admin=False, investment_id=2))
        db.session.add(Worker(position="pos2", admin=False, investment_id=2))
        db.session.commit()

        worker1 = Worker.query.get(1)
        worker2 = Worker.query.get(2)
        worker3 = Worker.query.get(3)

        assert Worker.get_team(investment_id=1) == [worker1, worker2, worker3]

    @staticmethod
    def test_get_new_tasks(add_tasks):
        user = User.query.filter_by(username="active_user").first()
        investment = Investment.query.filter_by(name="Test Invest").first()
        worker = Worker.get_by_username(investment.id, user.username)
        assert worker.last_time_tasks_displayed
        assert worker.get_new_tasks()

    @staticmethod
    def test_get_coming_tasks(add_tasks):
        user = User.query.filter_by(username="active_user").first()
        investment = Investment.query.filter_by(name="Test Invest").first()
        worker = Worker.get_by_username(investment.id, user.username)
        task = Task.query.filter_by(description="test task 2").first()
        assert worker.get_coming_tasks() == [task]


class TestInvestment:
    @staticmethod
    def test_investment(app_and_db, active_user):
        db = app_and_db[1]

        investment = Investment(name="Test Investment")
        user = User.query.filter_by(username="active_user").first()
        worker = Worker(position="test position", user_id=user.id)
        investment.workers.append(worker)
        db.session.add(investment)
        db.session.commit()

        user = User.query.filter_by(username="active_user").first()
        worker = Worker.query.filter_by(position="test position").first()
        investment = Investment.query.filter_by(name="Test Investment").first()

        assert user.workers.first() == worker
        assert investment.workers.first() == worker
        assert worker.user_id == user.id
        assert worker.investment_id == investment.id

    @staticmethod
    def test_get_by_user_id(app_and_db, active_user):
        db = app_and_db[1]
        investment = Investment(name="test")
        user = User.query.filter_by(username="active_user").first()
        worker = Worker(position="test worker", user_id=user.id)
        investment.workers.append(worker)
        db.session.add(investment)
        db.session.commit()

        assert Investment.get_by_user_id(user_id=1)

    @staticmethod
    def test_get_by_user_id_when_no_user(app_and_db):
        assert not Investment.get_by_user_id(user_id=1)

    @staticmethod
    def test_get_current_invest(app_and_db, active_user):
        db = app_and_db[1]

        investment = Investment(name="Test Investment")
        user = User.query.filter_by(username="active_user").first()
        user.current_invest_id = 1
        worker = Worker(position="test position", user_id=user.id)
        investment.workers.append(worker)
        db.session.add(investment)
        db.session.commit()

        user = User.query.filter_by(username="active_user").first()
        current_invest = user.get_current_invest()
        print(type(current_invest))
        assert current_invest.name == "Test Investment"

    @staticmethod
    def test_get_current_invest_when_no_investment(app_and_db, active_user):
        user = User.query.filter_by(username="active_user").first()
        current_invest = user.get_current_invest()
        assert current_invest.name == None

    @staticmethod
    def test_get_num_of_admins(app_and_db):
        db = app_and_db[1]
        for i in range(1, 4):
            user = User(
                username="user_{}".format(i),
                email="user_{}@mail.com".format(i),
                password="password",
            )
            user.is_active = True
            db.session.add(user)
        investment = Investment(name="test invest")
        db.session.add(investment)
        db.session.commit()

        user1 = User.get_user(1)
        user2 = User.get_user(2)
        user3 = User.get_user(3)
        invest = Investment.query.filter_by(id=1).first()
        worker1 = Worker(position="pos1", admin=True, user_id=user1.id)
        worker2 = Worker(position="pos2", admin=False, user_id=user2.id)
        worker3 = Worker(position="pos3", admin=True, user_id=user3.id)
        invest.workers.append(worker1)
        invest.workers.append(worker2)
        invest.workers.append(worker3)
        db.session.commit()

        assert Investment.get_num_of_admins(investment_id=1) == 2


class TestUser:
    @staticmethod
    def test_user(app_and_db):
        db = app_and_db[1]
        user = User("test_user", "user@gmail.com", "password")
        assert not user.is_active
        db.session.add(user)
        db.session.commit()
        user = User.query.filter_by(username="test_user").first()
        assert not user.is_active
        assert user.id

    @staticmethod
    def test_get_investment(app_and_db, active_user):
        db = app_and_db[1]
        user = User.get_user(1)
        db.session.add(Investment(name="test invest 1"))
        db.session.add(Investment(name="test invest 2"))
        db.session.commit()

        invest1 = Investment.query.filter_by(id=1).first()
        invest1.workers.append(Worker(user_id=user.id))
        invest2 = Investment.query.filter_by(id=2).first()
        invest2.workers.append(Worker(user_id=user.id))
        db.session.commit()

        assert User.get_investments(user_id=1) == [invest1, invest2]

    @staticmethod
    def test_get_investment_when_no_investments(app_and_db):
        assert type(User.get_investments(1)) == list

    @staticmethod
    def test_check_admins(app_and_db):
        db = app_and_db[1]

        for i in range(1, 5):
            user = User(
                username="user_{}".format(i),
                email="user_{}@mail.com".format(i),
                password="password",
            )
            user.is_active = True
            db.session.add(user)
            investment = Investment(name="test invest {}".format(i))
            db.session.add(investment)
            db.session.commit()

        user1 = Investment.query.filter_by(id=1).first()
        user2 = Investment.query.filter_by(id=2).first()
        user3 = Investment.query.filter_by(id=3).first()

        # one user -> not add to list
        invest1 = Investment.query.filter_by(id=1).first()
        worker1 = Worker(position="pos1", admin=True, user_id=user1.id)
        invest1.workers.append(worker1)

        # two users, one admin, user1 is admin -> add to list
        invest2 = Investment.query.filter_by(id=2).first()
        worker1 = Worker(position="pos1", admin=True, user_id=user1.id)
        worker2 = Worker(position="pos2", admin=False, user_id=user2.id)
        invest2.workers.append(worker1)
        invest2.workers.append(worker2)

        # two users, user1 is not admin -> not add to list
        invest3 = Investment.query.filter_by(id=3).first()
        worker1 = Worker(position="pos1", admin=False, user_id=user1.id)
        worker2 = Worker(position="pos2", admin=True, user_id=user2.id)
        invest3.workers.append(worker1)
        invest3.workers.append(worker2)

        # three user, two admin, user1 is admin -> not add to list
        invest4 = Investment.query.filter_by(id=4).first()
        worker1 = Worker(position="pos1", admin=True, user_id=user1.id)
        worker2 = Worker(position="pos2", admin=False, user_id=user2.id)
        worker3 = Worker(position="pos3", admin=True, user_id=user3.id)
        invest4.workers.append(worker1)
        invest4.workers.append(worker2)
        invest4.workers.append(worker3)

        db.session.commit()

        user = User.query.filter_by(username="user_1").first()
        assert User.check_admins(user_id=user.id)[0] == [invest2]
        assert User.check_admins(user_id=user.id)[1] == [invest1]

    @staticmethod
    def test_get_workers(app_and_db):
        db = app_and_db[1]
        user1 = User(
            username="test_user_1", email="test_user_1@gmail.com", password="password"
        )
        user2 = User(
            username="test_user_2", email="test_user_2@gmail.com", password="password"
        )
        db.session.add(user1)
        db.session.add(user2)
        db.session.add(Investment(name="test invest 1"))
        db.session.add(Investment(name="test invest 2"))
        db.session.add(Investment(name="test invest 3"))
        db.session.commit()

        user1 = User.get_user(1)
        invest1 = Investment.query.filter_by(id=1).first()
        invest1.workers.append(Worker(position="pos1", user_id=user1.id))
        invest2 = Investment.query.filter_by(id=2).first()
        invest2.workers.append(Worker(position="pos2", user_id=user1.id))

        user2 = User.get_user(2)
        invest3 = Investment.query.filter_by(id=3).first()
        invest3.workers.append(Worker(position="pos3", user_id=user2.id))

        db.session.commit()

        worker1 = Worker.query.filter_by(position="pos1").first()
        worker2 = Worker.query.filter_by(position="pos2").first()

        assert User.get_workers(user_id=1) == [worker1, worker2]


class TestTask:
    @staticmethod
    def test_task(add_tasks):
        investment = Investment.query.first()
        worker1 = Worker.query.filter_by(position="admin").first()
        worker2 = Worker.query.filter_by(position="second worker").first()
        task1 = Task.query.filter_by(description="test task 1").first()
        task2 = Task.query.filter_by(description="test task 2").first()
        task3 = Task.query.filter_by(description="test task 3").first()

        assert worker1.deputed_tasks.all() == [task1, task2, task3]
        assert worker1.tasks_to_execution.all() == [task2, task3]
        assert worker2.deputed_tasks.all() == []
        assert worker2.tasks_to_execution.all() == [task1]
        assert investment.tasks.all() == [task1, task2, task3]
