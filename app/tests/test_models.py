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
    Wall.add_item(**kwargs)
    assert Wall.get_all_items()


def test_add_processing(app, add_wall):
    wall_id = Wall.get_all_items()[0].id
    Wall.add_processing(wall_id, year=2020, month="December", done=0.4)
    Wall.add_processing(wall_id, year=2020, month="December", done=0.5)
    wall = Wall.query.filter_by(id=wall_id).first()
    assert wall.left_to_sale == "0.1"


def test_add_processing_when_overrun(app, add_wall):
    wall_id = Wall.get_all_items()[0].id
    Wall.add_processing(wall_id, year=2020, month="December", done=0.4)
    Wall.add_processing(wall_id, year=2020, month="December", done=0.7)
    wall = Wall.query.filter_by(id=wall_id).first()
    assert wall.left_to_sale == "0"


def test_calculate_rest_attributes_hole():
    hole = Hole(width=1.2, height=2.0, amount=2)
    hole.calculate_rest_attributes()
    assert hole.area == 2.4
    assert hole.total_area == 4.8


def test_calculate_rest_attributes_wall(add_wall):
    wall = Wall.get_all_items()[0]
    Wall.add_hole(wall.id, hole_width=1.2, hole_height=2.0, holes_amount=2)
    Wall.add_hole(wall.id, hole_width=2.2, hole_height=2.0, holes_amount=1)
    Wall.add_processing(wall.id, year=2020, month="December", done=0.4)
    assert wall.wall_height == "3.1"
    assert wall.gross_wall_area == "32.55"
    assert wall.wall_area_to_survey == "23.35"
    assert wall.wall_area_to_sale == "29.15"
    assert wall.left_to_sale == "0.6"


def test_update_wall(app):
    # TODO finish updating items
    pass


def test_update_hole(app):
    # TODO finish updating items
    pass


def test_update_processing(app):
    # TODO finish updating items
    pass
