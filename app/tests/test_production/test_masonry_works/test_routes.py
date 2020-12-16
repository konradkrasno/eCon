import pytest

from app.models import Wall, Hole, Processing
from app.tests.conftest import assert_flashes
from app.production.masonry_works.forms import ProcessingForm


def test_walls(client, captured_templates):
    response = client.get("/production/walls")
    assert response.status_code == 200
    assert len(captured_templates) == 1
    template, context = captured_templates[0]
    assert template.name == "production/masonry_works/walls.html"
    assert context["title"] == "Walls"
    assert context["items"] == Wall.get_all_items()
    assert context["wall_header"] == Wall.get_header()


def test_holes(client, captured_templates):
    response = client.get("/production/holes/1")
    assert response.status_code == 200
    assert len(captured_templates) == 1
    template, context = captured_templates[0]
    assert template.name == "production/masonry_works/holes.html"
    assert context["title"] == "Holes"
    assert context["items"] == Hole.get_all_items(1)
    assert context["hole_header"] == Hole.get_header()


def test_processing(client, captured_templates):
    response = client.get("/production/processing/1")
    assert response.status_code == 200
    assert len(captured_templates) == 1
    template, context = captured_templates[0]
    assert template.name == "production/masonry_works/processing.html"
    assert context["title"] == "Processing"
    assert context["items"] == Processing.get_all_items(1)
    assert context["processing_header"] == Processing.get_header()


def test_add_wall(client, captured_templates, wall_data):
    response = client.post("/production/add_wall", data=wall_data, follow_redirects=True)
    assert response.status_code == 200
    assert len(captured_templates) == 1
    template, context = captured_templates[0]
    assert template.name == "production/masonry_works/forms/wall_form.html"
    assert context["title"] == "Wall Form"
    assert context["form"].object.data == "G"
    assert context["form"].level.data == "2"
    # assert context["form"].validate_on_submit()
    # assert_flashes(client, "You added a new wall.")


def test_add_hole(client):
    pass


def test_add_processing(client, captured_templates):
    # form = ProcessingForm(year=2020, month="September", done=0.5)
    # form.submit()
    response = client.post(
        "/production/add_processing/1",
        # data = form.data,
        data={"year": 2020, "month": "September", "done": 0.5},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert len(captured_templates) == 1
    template, context = captured_templates[0]
    assert template.name == "production/masonry_works/forms/processing_form.html"
    assert context["title"] == "Processing Form"
    assert context["form"].year.data == 2020
    assert context["form"].month.data == "September"
    assert context["form"].done.data == 0.5
    # assert context["form"].validate_on_submit()
    # assert_flashes(client, "You added a new processing.")


def test_edit_masonry_item(client):
    # TODO finish updating items
    pass


def test_delete_masonry_item(client):
    # TODO add deleting items
    pass
