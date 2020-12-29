import pytest

from app.models import User, Investment, Hole, Processing, Wall


def test_create_item_when_wrong_attribute(wall_data):
    wall_data["wrong_attr"] = 5
    item = Wall.create_item(**wall_data)
    assert item


def test_update_item(wall_data):
    wall = Wall(**wall_data)
    wall = Wall.update_item(wall, object="K", level=5)
    assert wall.object == "K"
    assert wall.level == 5


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


def test_create_processing(app_and_db):
    app, db = app_and_db
    processing = Processing(year=2020, month="December", done=0.4)
    db.session.add(processing)
    db.session.commit()
    processing = Processing.query.filter_by(id=1).first()
    assert processing.done == 0.4


def test_create_processing_with_done_above_1():
    with pytest.raises(ValueError):
        Processing(year=2020, month="December", done=1.2)


def test_edit_processing(app_and_db):
    app, db = app_and_db
    processing = Processing(year=2020, month="December", done=0.4)
    processing.done = 0.6
    db.session.add(processing)
    db.session.commit()
    processing = Processing.query.filter_by(id=1).first()
    assert processing.done == 0.6


def test_edit_processing_with_done_above_1():
    processing = Processing(year=2020, month="December", done=0.4)
    with pytest.raises(ValueError):
        processing.done = 1.2


def test_add_wall(app_and_db, wall_data):
    Wall.add_wall(**wall_data)
    wall = Wall.get_all_items()[0]
    Wall.add_hole(wall.id, width=1.2, height=2.0, amount=2)
    Wall.add_hole(wall.id, width=2.2, height=2.0, amount=1)
    Wall.add_processing(wall.id, year=2020, month="December", done=0.4)
    assert wall.wall_height == 3.1
    assert wall.gross_wall_area == 32.55
    assert wall.wall_area_to_survey == 23.35
    assert wall.wall_area_to_sale == 29.15
    assert wall.left_to_sale == 0.6


def test_add_hole_without_height(add_wall):
    wall = Wall.get_all_items()[0]
    Wall.add_hole(wall.id, width=1.2, amount=2)
    hole = Hole.query.first()
    assert hole.height == None
    with pytest.raises(ValueError):
        assert hole.area


def test_add_processing(add_wall):
    wall = Wall.get_all_items()[0]
    assert wall.left_to_sale == 1.0
    Wall.add_processing(wall.id, year=2020, month="December", done=0.4)
    Wall.add_processing(wall.id, year=2020, month="December", done=0.5)
    assert wall.left_to_sale == 0.1


def test_add_processing_when_overrun(add_wall):
    wall_id = Wall.get_all_items()[0].id
    Wall.add_processing(wall_id, year=2020, month="December", done=0.4)
    Wall.add_processing(wall_id, year=2020, month="December", done=0.7)
    wall = Wall.query.filter_by(id=wall_id).first()
    assert wall.processing.filter_by(id=1).first().done == 0.4
    assert wall.processing.filter_by(id=2).first().done == 0.6
    assert wall.left_to_sale == 0.0


def test_add_processing_when_done_above_1(add_wall):
    wall_id = Wall.get_all_items()[0].id
    Wall.add_processing(wall_id, year=2020, month="December", done=2)
    wall = Wall.query.filter_by(id=wall_id).first()
    assert wall.processing[0].done == 1.0
    assert wall.left_to_sale == 0.0


def test_update_item_when_wrong_attr(wall_data):
    wall = Wall(**wall_data)
    wall = Wall.update_item(wall, wrong_attr1="K", wrong_attr2=5)
    assert wall.sector == "G"
    assert wall.level == 2


def test_update_wall(add_wall):
    wall = Wall.get_all_items()[0]
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


def test_update_hole(add_wall):
    wall = Wall.get_all_items()[0]
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


def test_update_processing(add_wall):
    wall = Wall.get_all_items()[0]
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


def test_update_processing_when_overrun(add_wall):
    wall = Wall.get_all_items()[0]
    Wall.add_processing(wall.id, year=2020, month="December", done=0.6)
    Wall.add_processing(wall.id, year=2020, month="December", done=0.3)
    assert wall.processing.filter_by(id=1).first().done == 0.6
    assert wall.processing.filter_by(id=2).first().done == 0.3
    assert wall.left_to_sale == 0.1
    Wall.edit_processing(2, done=0.5)
    assert wall.processing.filter_by(id=1).first().done == 0.6
    assert wall.processing.filter_by(id=2).first().done == 0.4
    assert wall.left_to_sale == 0.0


def test_update_processing_when_done_above_1(add_wall):
    wall = Wall.get_all_items()[0]
    Wall.add_processing(wall.id, year=2020, month="December", done=0.6)
    processing = wall.processing[0]
    Wall.edit_processing(processing.id, done=1.35)
    assert wall.processing[0].done == 1.0
    assert wall.left_to_sale == 0.0


def test_delete_wall(add_wall):
    Wall.add_hole(wall_id=1, width=1, height=2, amonunt=1)
    Wall.add_processing(wall_id=1, year=2020, month="December", done=0.5)
    assert Wall.query.filter_by(id=1).first()
    Wall.delete_wall(1)
    assert not Wall.query.filter_by(id=1).first()


def test_delete_wall_when_no_wall(app_and_db):
    assert not Wall.query.filter_by(id=1).first()
    Wall.delete_wall(1)


def test_delete_hole(add_wall):
    Wall.add_hole(wall_id=1, width=1, height=2, amonunt=1)
    assert Hole.query.filter_by(id=1).first()
    Wall.delete_hole(1)
    assert not Hole.query.filter_by(id=1).first()


def test_delete_hole_when_no_hole(app_and_db):
    assert not Hole.query.filter_by(id=1).first()
    Wall.delete_hole(1)


def test_delete_processing(add_wall):
    Wall.add_processing(wall_id=1, year=2020, month="December", done=0.5)
    assert Processing.query.filter_by(id=1).first()
    Wall.delete_processing(1)
    assert not Processing.query.filter_by(id=1).first()


def test_delete_processing_when_no_processing(app_and_db):
    assert not Processing.query.filter_by(id=1).first()
    Wall.delete_processing(1)


def test_upload_walls(app_and_db):
    messages = Wall.upload_walls("test/walls.csv")
    assert len(Wall.query.all()) == 5
    assert len(messages) == 2
    assert messages[0] == "Uploaded 6 items."
    assert (
        messages[1]
        == "Items: [8, 9, 10, 11, 12, 13, 14, 15] not added because they has the wrong format."
    )
    assert Wall.query.filter_by(id=1).first().wall_width == 18


def test_upload_walls_when_wrong_file(app_and_db):
    messages = Wall.upload_walls("test/holes.csv")
    assert len(Wall.query.all()) == 0
    assert len(messages) == 2
    assert messages[0] == "Uploaded 0 items."


def test_upload_holes(app_and_db):
    Wall.upload_walls("test/walls.csv")
    Wall.upload_holes("test/holes.csv")
    messages = Wall.upload_holes("test/holes.csv")
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


def test_upload_processing(app_and_db):
    Wall.upload_walls("test/walls.csv")
    Wall.upload_processing("test/processing.csv")
    messages = Wall.upload_processing("test/processing.csv")
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
    assert messages[3] == "Items: [1, 3] not added because value of left_to_sale is 0."


def test_user(app_and_db):
    db = app_and_db[1]
    user = User("test_user", "user@gmail.com", "password")
    assert not user.is_active
    db.session.add(user)
    db.session.commit()
    user = User.query.filter_by(username="test_user").first()
    assert not user.is_active
    assert user.id


def test_get_user():
    assert not User.get_user(None)
