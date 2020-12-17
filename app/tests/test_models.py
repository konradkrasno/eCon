import pytest

from app.models import User, Investment, Hole, Processing, Wall


def test_add_wall(app):
    kwargs = {
        "object": "K",
        "level": 2,
        "localization": "O/5",
        "brick_type": "YTONG",
        "wall_width": 24,
        "wall_length": 10.5,
        "floor_ord": 0,
        "ceiling_ord": 3.10,
    }
    Wall.add_wall(**kwargs)
    assert Wall.get_all_items()


def test_add_processing(add_wall):
    wall = Wall.get_all_items()[0]
    assert wall.left_to_sale == "1.0"
    Wall.add_processing(wall.id, year=2020, month="December", done=0.4)
    Wall.add_processing(wall.id, year=2020, month="December", done=0.5)
    assert wall.left_to_sale == "0.1"


def test_add_processing_when_overrun(add_wall):
    wall_id = Wall.get_all_items()[0].id
    Wall.add_processing(wall_id, year=2020, month="December", done=0.4)
    Wall.add_processing(wall_id, year=2020, month="December", done=0.7)
    wall = Wall.query.filter_by(id=wall_id).first()
    assert wall.processing[0].done == "0.4"
    assert wall.processing[1].done == "0.6"
    assert wall.left_to_sale == "0"


def test_add_processing_when_above_1_added(add_wall):
    wall_id = Wall.get_all_items()[0].id
    Wall.add_processing(wall_id, year=2020, month="December", done=2)
    wall = Wall.query.filter_by(id=wall_id).first()
    assert wall.processing[0].done == "1"
    assert wall.left_to_sale == "0"


def test_calculate_rest_attributes_hole():
    hole = Hole(width=1.2, height=2.0, amount=2)
    hole.calculate_rest_attributes()
    assert hole.area == 2.4
    assert hole.total_area == 4.8


def test_calculate_rest_attributes_wall(add_wall):
    wall = Wall.get_all_items()[0]
    Wall.add_hole(wall.id, width=1.2, height=2.0, amount=2)
    Wall.add_hole(wall.id, width=2.2, height=2.0, amount=1)
    Wall.add_processing(wall.id, year=2020, month="December", done=0.4)
    assert wall.wall_height == "3.1"
    assert wall.gross_wall_area == "32.55"
    assert wall.wall_area_to_survey == "23.35"
    assert wall.wall_area_to_sale == "29.15"
    assert wall.left_to_sale == "0.6"


def test_create_item_when_wrong_attribute(wall_data):
    wall_data["wrong_attr"] = 5
    item = Wall.create_item(Wall, **wall_data)
    assert item


def test_update_item(wall_data):
    wall = Wall(**wall_data)
    wall = Wall.update_item(wall, object="K", level=5)
    assert wall.object == "K"
    assert wall.level == 5


def test_update_item_when_wrong_attr(wall_data):
    wall = Wall(**wall_data)
    wall = Wall.update_item(wall, wrong_attr1="K", wrong_attr2=5)
    assert wall.object == "G"
    assert wall.level == 2


def test_update_wall(add_wall):
    wall = Wall.get_all_items()[0]
    assert wall.wall_height == "3.1"
    assert wall.gross_wall_area == "32.55"
    assert wall.wall_area_to_survey == "32.55"
    assert wall.wall_area_to_sale == "32.55"
    assert wall.left_to_sale == "1.0"
    Wall.edit_wall(wall.id, floor_ord=4)
    assert wall.wall_height == "2.2"
    assert wall.gross_wall_area == "23.1"
    assert wall.wall_area_to_survey == "23.1"
    assert wall.wall_area_to_sale == "23.1"
    assert wall.left_to_sale == "1.0"


def test_update_hole(add_wall):
    wall = Wall.get_all_items()[0]
    Wall.add_hole(wall.id, width=1.2, height=2.0, amount=2)
    assert wall.holes[0].width == "1.2"
    assert wall.holes[0].height == "2.0"
    assert wall.holes[0].amount == 2
    assert wall.wall_area_to_survey == "27.75"
    hole = wall.holes[0]
    Wall.edit_hole(hole.id, width=1.5, height=2.5, amount=1)
    assert wall.holes[0].width == "1.5"
    assert wall.holes[0].height == "2.5"
    assert wall.holes[0].amount == 1
    assert wall.wall_area_to_survey == "28.8"


def test_update_processing(add_wall):
    wall = Wall.get_all_items()[0]
    Wall.add_processing(wall.id, year=2020, month="December", done=0.3)
    assert wall.processing[0].year == 2020
    assert wall.processing[0].month == "December"
    assert wall.processing[0].done == "0.3"
    assert wall.left_to_sale == "0.7"
    processing = wall.processing[0]
    Wall.edit_processing(processing.id, month="November", done=0.6)
    assert wall.processing[0].year == 2020
    assert wall.processing[0].month == "November"
    assert wall.processing[0].done == "0.6"
    assert wall.left_to_sale == "0.4"


@pytest.mark.parametrize("done", [0.5, 1.5])
def test_update_processing_when_overrun(add_wall, done):
    wall = Wall.get_all_items()[0]
    Wall.add_processing(wall.id, year=2020, month="December", done=0.6)
    Wall.add_processing(wall.id, year=2020, month="December", done=0.3)
    assert wall.processing[0].done == "0.6"
    assert wall.processing[1].done == "0.3"
    assert wall.left_to_sale == "0.1"
    processing = wall.processing[-1]
    Wall.edit_processing(processing.id, done=done)
    assert wall.processing[1].done == "0.6"
    assert wall.processing[0].done == "0.4"
    assert wall.left_to_sale == "0.0"
