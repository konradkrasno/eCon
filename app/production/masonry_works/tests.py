from flask import url_for
from flask_login import current_user
from app.production.masonry_works.data_treatment import Categories, TotalAreas
from app.models import Wall, Hole, Processing, Investment
from app.production.masonry_works.forms import (
    WallForm,
    HoleForm,
    ProcessingForm,
)
from app.main.forms import WarrantyForm


class TestWalls:
    @staticmethod
    def test_get(client, captured_templates, test_with_authenticated_user, add_wall):
        investment = Investment.query.filter_by(name="Test Invest").first()
        current_user.current_invest_id = investment.id
        response = client.get(url_for("masonry_works.walls"))
        assert response.status_code == 200
        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "production/masonry_works/walls.html"
        assert context["title"] == "Walls"
        assert context["items"] == Wall.query.all()
        assert isinstance(context["total"], TotalAreas)
        assert isinstance(context["categories"], Categories)


class TestHoles:
    @staticmethod
    def test_get(
        client, captured_templates, test_with_authenticated_user, add_wall, add_hole
    ):
        wall = Wall.query.first()
        response = client.get(url_for("masonry_works.holes", wall_id=wall.id))
        assert response.status_code == 200
        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "production/masonry_works/holes.html"
        assert context["title"] == "Holes"
        assert context["items"] == Hole.query.all()
        assert context["wall_id"] == str(wall.id)


class TestProcessing:
    @staticmethod
    def test_get(
        client,
        captured_templates,
        test_with_authenticated_user,
        add_wall,
        add_processing,
    ):
        wall = Wall.query.first()
        response = client.get(url_for("masonry_works.processing", wall_id=wall.id))
        assert response.status_code == 200
        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "production/masonry_works/processing.html"
        assert context["title"] == "Processing"
        assert context["items"] == Processing.query.all()
        assert context["wall_id"] == str(wall.id)


class TestModify:
    @staticmethod
    def test_get(client, captured_templates, test_with_authenticated_user, add_wall):
        wall = Wall.query.first()
        response = client.get(url_for("masonry_works.modify", wall_id=wall.id))
        assert response.status_code == 200
        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "production/masonry_works/modify.html"
        assert context["title"] == "Modify"
        assert context["item"] == wall


class TestAddWall:
    @staticmethod
    def test_get(client, captured_templates, test_with_authenticated_user):
        response = client.get(url_for("masonry_works.add_wall"))
        assert response.status_code == 200
        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "production/masonry_works/forms/wall_form.html"
        assert context["title"] == "Add Wall"
        assert isinstance(context["form"], WallForm)

    @staticmethod
    def test_post(client, test_with_authenticated_user, wall_data):
        form = WallForm(**wall_data)
        assert not Wall.query.all()
        response = client.post(
            url_for("masonry_works.add_wall"), data=form.data, follow_redirects=True
        )
        assert response.status_code == 200
        assert b"You added a new wall." in response.data
        assert Wall.query.all()


class TestAddHole:
    @staticmethod
    def test_get(client, captured_templates, test_with_authenticated_user):
        response = client.get(url_for("masonry_works.add_hole"))
        assert response.status_code == 200
        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "production/masonry_works/forms/hole_form.html"
        assert context["title"] == "Add Hole"
        assert isinstance(context["form"], HoleForm)

    @staticmethod
    def test_post(client, test_with_authenticated_user, add_wall):
        wall = Wall.query.first()
        form = HoleForm(width=1.2, height=2.25, amount=2)
        assert not Hole.query.all()
        response = client.post(
            url_for("masonry_works.add_hole", wall_id=wall.id),
            data=form.data,
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"You added a new hole." in response.data
        assert Hole.query.all()


class TestAddProcessing:
    @staticmethod
    def test_get(client, captured_templates, test_with_authenticated_user):
        response = client.get(url_for("masonry_works.add_processing"))
        assert response.status_code == 200
        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "production/masonry_works/forms/processing_form.html"
        assert context["title"] == "Add Processing"
        assert isinstance(context["form"], ProcessingForm)

    @staticmethod
    def test_post(client, test_with_authenticated_user, add_wall):
        wall = Wall.query.first()
        form = ProcessingForm(year=2020, month="December", done=0.4)
        assert not Processing.query.all()
        response = client.post(
            url_for("masonry_works.add_processing", wall_id=wall.id),
            data=form.data,
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"You added a new processing." in response.data
        assert Processing.query.all()


class TestEditWall:
    @staticmethod
    def test_get(client, captured_templates, test_with_authenticated_user, add_wall):
        wall = Wall.query.first()
        response = client.get(url_for("masonry_works.edit_wall", wall_id=wall.id))
        assert response.status_code == 200
        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "production/masonry_works/forms/wall_form.html"
        assert context["title"] == "Edit Wall"
        assert isinstance(context["form"], WallForm)
        assert context["form"].sector.data == wall.sector
        assert context["form"].level.data == wall.level
        assert context["form"].localization.data == wall.localization
        assert context["form"].brick_type.data == wall.brick_type
        assert context["form"].wall_width.data == wall.wall_width
        assert context["form"].wall_length.data == wall.wall_length
        assert context["form"].floor_ord.data == wall.floor_ord
        assert context["form"].ceiling_ord.data == wall.ceiling_ord

    @staticmethod
    def test_post(client, test_with_authenticated_user, wall_data):
        Wall.add_wall(**wall_data)
        wall_data["sector"] = "A"
        form = WallForm(**wall_data)
        wall = Wall.query.first()
        assert wall.sector == "G"
        response = client.post(
            url_for("masonry_works.edit_wall", wall_id=wall.id),
            data=form.data,
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"You modified the wall." in response.data
        assert wall.sector == "A"


class TestEditHole:
    @staticmethod
    def test_get(
        client, captured_templates, test_with_authenticated_user, add_wall, add_hole
    ):
        wall = Wall.query.first()
        hole = wall.holes.first()
        response = client.get(
            url_for("masonry_works.edit_hole", wall_id=wall.id, hole_id=hole.id)
        )
        assert response.status_code == 200
        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "production/masonry_works/forms/hole_form.html"
        assert context["title"] == "Edit Hole"
        assert isinstance(context["form"], HoleForm)
        assert context["form"].width.data == hole.width
        assert context["form"].height.data == hole.height
        assert context["form"].amount.data == hole.amount

    @staticmethod
    def test_post(client, test_with_authenticated_user, add_wall, add_hole):
        wall = Wall.query.first()
        hole = wall.holes.first()
        assert hole.height == 2.25
        form = HoleForm(width=1.2, height=1.25, amount=2)
        response = client.post(
            url_for("masonry_works.edit_hole", wall_id=wall.id, hole_id=hole.id),
            data=form.data,
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"You modified the hole." in response.data
        assert hole.height == 1.25


class TestEditProcessing:
    @staticmethod
    def test_get(
        client,
        captured_templates,
        test_with_authenticated_user,
        add_wall,
        add_processing,
    ):
        wall = Wall.query.first()
        processing = wall.processing.first()
        response = client.get(
            url_for(
                "masonry_works.edit_processing", wall_id=wall.id, proc_id=processing.id
            )
        )
        assert response.status_code == 200
        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "production/masonry_works/forms/processing_form.html"
        assert context["title"] == "Edit Processing"
        assert isinstance(context["form"], ProcessingForm)
        assert context["form"].year.data == processing.year
        assert context["form"].month.data == processing.month
        assert context["form"].done.data == processing.done

    @staticmethod
    def test_post(client, test_with_authenticated_user, add_wall, add_processing):
        wall = Wall.query.first()
        processing = wall.processing.first()
        assert processing.done == 0.4
        form = ProcessingForm(year=2020, month="December", done=0.8)
        response = client.post(
            url_for(
                "masonry_works.edit_processing", wall_id=wall.id, proc_id=processing.id
            ),
            data=form.data,
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"You modified the processing." in response.data
        assert processing.done == 0.8


class TestDeleteWall:
    @staticmethod
    def test_get(client, captured_templates, test_with_authenticated_user, add_wall):
        wall = Wall.query.first()
        response = client.get(url_for("masonry_works.delete_wall", wall_id=wall.id))
        assert response.status_code == 200
        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "warranty_form.html"
        assert context["title"] == "Delete Wall"
        assert isinstance(context["form"], WarrantyForm)

    @staticmethod
    def test_post_when_no(
        client, captured_templates, test_with_authenticated_user, add_wall
    ):
        wall = Wall.query.first()
        response = client.post(
            url_for(
                "masonry_works.delete_wall",
                wall_id=wall.id,
                next_page=url_for("main.index"),
            ),
            data={"no": True},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Wall has not been deleted." in response.data
        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "index.html"

    @staticmethod
    def test_post_when_yes(client, test_with_authenticated_user, add_wall):
        wall = Wall.query.first()
        assert Wall.query.first()
        response = client.post(
            url_for("masonry_works.delete_wall", wall_id=wall.id),
            data={"yes": True},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Wall has been deleted." in response.data
        assert not Wall.query.first()


class TestDeleteHole:
    @staticmethod
    def test_get(
        client, captured_templates, test_with_authenticated_user, add_wall, add_hole
    ):
        wall = Wall.query.first()
        hole = Hole.query.first()
        response = client.get(
            url_for("masonry_works.delete_hole", wall_id=wall.id, hole_id=hole.id)
        )
        assert response.status_code == 200
        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "warranty_form.html"
        assert context["title"] == "Delete Hole"
        assert isinstance(context["form"], WarrantyForm)

    @staticmethod
    def test_post_when_no(client, test_with_authenticated_user, add_wall, add_hole):
        wall = Wall.query.first()
        hole = Hole.query.first()
        response = client.post(
            url_for(
                "masonry_works.delete_hole",
                wall_id=wall.id,
                hole_id=hole.id,
            ),
            data={"no": True},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Hole has not been deleted." in response.data

    @staticmethod
    def test_post_when_yes(client, test_with_authenticated_user, add_wall, add_hole):
        wall = Wall.query.first()
        hole = Hole.query.first()
        assert Hole.query.first()
        response = client.post(
            url_for("masonry_works.delete_hole", wall_id=wall.id, hole_id=hole.id),
            data={"yes": True},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Hole has been deleted." in response.data
        assert not Hole.query.first()


class TestDeleteProcessing:
    @staticmethod
    def test_get(
        client,
        captured_templates,
        test_with_authenticated_user,
        add_wall,
        add_processing,
    ):
        wall = Wall.query.first()
        processing = Processing.query.first()
        response = client.get(
            url_for(
                "masonry_works.delete_processing",
                wall_id=wall.id,
                proc_id=processing.id,
            )
        )
        assert response.status_code == 200
        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "warranty_form.html"
        assert context["title"] == "Delete Processing"
        assert isinstance(context["form"], WarrantyForm)

    @staticmethod
    def test_post_when_no(
        client, test_with_authenticated_user, add_wall, add_processing
    ):
        wall = Wall.query.first()
        processing = Processing.query.first()
        response = client.post(
            url_for(
                "masonry_works.delete_processing",
                wall_id=wall.id,
                proc_id=processing.id,
            ),
            data={"no": True},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Processing has not been deleted." in response.data

    @staticmethod
    def test_post_when_yes(
        client, test_with_authenticated_user, add_wall, add_processing
    ):
        wall = Wall.query.first()
        processing = Processing.query.first()
        assert Processing.query.first()
        response = client.post(
            url_for(
                "masonry_works.delete_processing",
                wall_id=wall.id,
                proc_id=processing.id,
            ),
            data={"yes": True},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Processing has been deleted." in response.data
        assert not Processing.query.first()
