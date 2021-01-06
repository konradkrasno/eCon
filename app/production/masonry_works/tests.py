from flask import url_for
from app.models import Wall, Hole, Processing


def test_walls(client, captured_templates):
    response = client.get("/masonry_works/walls")
    assert response.status_code == 200
    assert len(captured_templates) == 1
    template, context = captured_templates[0]
    assert template.name == "production/masonry_works/walls.html"
    assert context["title"] == "Walls"
    assert context["items"] == Wall.get_all_items()


def test_holes(client, captured_templates):
    response = client.get("/masonry_works/holes")
    assert response.status_code == 200
    assert len(captured_templates) == 1
    template, context = captured_templates[0]
    assert template.name == "production/masonry_works/holes.html"
    assert context["title"] == "Holes"
    assert context["items"] == Hole.get_items_by_wall_id(1)


def test_processing(client, captured_templates):
    response = client.get("/masonry_works/processing")
    assert response.status_code == 200
    assert len(captured_templates) == 1
    template, context = captured_templates[0]
    assert template.name == "production/masonry_works/processing.html"
    assert context["title"] == "Processing"
    assert context["items"] == Processing.get_items_by_wall_id(1)


def test_add_wall(client, captured_templates, wall_data):
    response = client.post(
        "/masonry_works/add_wall", data=wall_data, follow_redirects=True
    )
    assert response.status_code == 200
    assert len(captured_templates) == 1
    template, context = captured_templates[0]
    assert template.name == "production/masonry_works/forms/wall_form.html"
    assert context["title"] == "Add Wall"
    assert context["form"].sector.data == "G"
    assert context["form"].level.data == "2"
    # assert context["form"].validate_on_submit()
    # assert_flashes(client, "You added a new wall.")


def test_add_hole(client):
    pass


def test_add_processing(client, captured_templates):
    # form = ProcessingForm(year=2020, month="September", done=0.5)
    # form.submit()
    response = client.post(
        "/masonry_works/add_processing",
        # data = form.data,
        data={"year": 2020, "month": "September", "done": 0.5},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert len(captured_templates) == 1
    template, context = captured_templates[0]
    assert template.name == "production/masonry_works/forms/processing_form.html"
    assert context["title"] == "Add Processing"
    assert context["form"].year.data == 2020
    assert context["form"].month.data == "September"
    assert context["form"].done.data == 0.5
    # assert context["form"].validate_on_submit()
    # assert_flashes(client, "You added a new processing.")


def test_edit_wall(client, captured_templates, add_wall):
    response = client.post(url_for("masonry_works.edit_wall", wall_id=1))
    assert response.status_code == 200
    assert len(captured_templates) == 1
    template, context = captured_templates[0]
    assert template.name == "production/masonry_works/forms/wall_form.html"
    assert context["title"] == "Edit Wall"
    assert context["form"].sector.data == "G"
    assert context["form"].level.data == "2"


def test_edit_hole():
    pass


def test_edit_processing():
    pass
