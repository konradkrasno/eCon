import pytest

from app.models import User, Investment, Hole, Processing, Wall


def test_create_item_when_wrong_attribute(wall_data):
    wall_data["wrong_attr"] = 5
    item = Wall.create_item(Wall, **wall_data)
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
    assert hole.width == "1.2"
    assert hole.height == "2"
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
    hole.width = "2.5"
    assert hole.width == "2.5"
    assert hole.height == "2"
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
    assert processing.done == "0.4"


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
    assert processing.done == "0.6"


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
    assert wall.processing.filter_by(id=1).first().done == "0.4"
    assert wall.processing.filter_by(id=2).first().done == "0.6"
    assert wall.left_to_sale == 0.0


def test_add_processing_when_done_above_1(add_wall):
    wall_id = Wall.get_all_items()[0].id
    with pytest.raises(ValueError):
        Wall.add_processing(wall_id, year=2020, month="December", done=2)


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
    assert wall.holes[0].width == "1.2"
    assert wall.holes[0].height == "2.0"
    assert wall.holes[0].amount == 2
    assert wall.wall_area_to_survey == 27.75
    hole = wall.holes[0]
    Wall.edit_hole(hole.id, width=1.5, height=2.5, amount=1)
    assert wall.holes[0].width == "1.5"
    assert wall.holes[0].height == "2.5"
    assert wall.holes[0].amount == 1
    assert wall.wall_area_to_survey == 28.8


def test_update_processing(add_wall):
    wall = Wall.get_all_items()[0]
    Wall.add_processing(wall.id, year=2020, month="December", done=0.3)
    assert wall.processing[0].year == 2020
    assert wall.processing[0].month == "December"
    assert wall.processing[0].done == "0.3"
    assert wall.left_to_sale == 0.7
    processing = wall.processing[0]
    Wall.edit_processing(processing.id, year=2021, month="January", done=0.6)
    assert wall.processing[0].year == 2021
    assert wall.processing[0].month == "January"
    assert wall.processing[0].done == "0.6"
    assert wall.left_to_sale == 0.4


def test_update_processing_when_overrun(add_wall):
    wall = Wall.get_all_items()[0]
    Wall.add_processing(wall.id, year=2020, month="December", done=0.6)
    Wall.add_processing(wall.id, year=2020, month="December", done=0.3)
    assert wall.processing.filter_by(id=1).first().done == "0.6"
    assert wall.processing.filter_by(id=2).first().done == "0.3"
    assert wall.left_to_sale == 0.1
    Wall.edit_processing(2, done=0.5)
    assert wall.processing.filter_by(id=1).first().done == "0.6"
    assert wall.processing.filter_by(id=2).first().done == "0.4"
    assert wall.left_to_sale == 0.0


def test_update_processing_when_done_above_1(add_wall):
    wall = Wall.get_all_items()[0]
    Wall.add_processing(wall.id, year=2020, month="December", done=0.6)
    processing = wall.processing[-1]
    with pytest.raises(ValueError):
        Wall.edit_processing(processing.id, done=1.35)


def test_delete_wall(add_wall):
    Wall.add_hole(wall_id=1, width=1, height=2, amonunt=1)
    Wall.add_processing(wall_id=1, year=2020, month="December", done=0.5)
    assert Wall.query.filter_by(id=1).first()
    Wall.delete_wall(1)
    assert not Wall.query.filter_by(id=1).first()


def test_delete_hole(add_wall):
    Wall.add_hole(wall_id=1, width=1, height=2, amonunt=1)
    assert Hole.query.filter_by(id=1).first()
    Wall.delete_hole(1)
    assert not Hole.query.filter_by(id=1).first()


def test_delete_processing(add_wall):
    Wall.add_processing(wall_id=1, year=2020, month="December", done=0.5)
    assert Processing.query.filter_by(id=1).first()
    Wall.delete_processing(1)
    assert not Processing.query.filter_by(id=1).first()
