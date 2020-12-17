from typing import *

from fractions import Fraction as frac
from app import db

investment_associate = db.Table(
    "investment_associate",
    db.Column("investment_id", db.Integer, db.ForeignKey("investment.id")),
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    investments = db.relationship(
        "Investment",
        secondary=investment_associate,
        primaryjoin=(investment_associate.c.investment_id == id),
        secondaryjoin=(investment_associate.c.user_id == id),
        backref=db.backref("investment_associate", lazy="dynamic"),
        lazy="dynamic",
    )

    def __repr__(self) -> str:
        return "<User(username=%s)>" % (self.username,)


class Investment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True, unique=True)
    workers = db.relationship(
        "User",
        secondary=investment_associate,
        primaryjoin=(investment_associate.c.investment_id == id),
        secondaryjoin=(investment_associate.c.user_id == id),
        backref=db.backref("investment_associate", lazy="dynamic"),
        lazy="dynamic",
    )
    # masonry_registry = db.relationship("Wall", backref="investment", lazy="dynamic")

    def __repr__(self) -> str:
        return "<Investment(name=%s)>" % (self.name,)


class Hole(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    width = db.Column(db.String(32))
    height = db.Column(db.String(32))
    amount = db.Column(db.Integer)
    area = db.Column(db.String(32))
    total_area = db.Column(db.String(32))
    below_3m2 = db.Column(db.Boolean)
    wall_id = db.Column(db.Integer, db.ForeignKey("wall.id", ondelete="CASCADE"))

    @staticmethod
    def get_header() -> List:
        return [
            "Hole width",
            "Hole height",
            "Holes amount",
            "Hole area",
            "Holes area",
            "Hole below 3 square metres",
        ]

    def calculate_rest_attributes(self) -> None:
        area = frac(self.width) * frac(self.height)
        total_area = area * frac(self.amount)
        self.area = float(area)
        self.total_area = float(total_area)
        self.below_3m2 = True if self.area < frac(3) else False

    @classmethod
    def get_items_by_wall_id(cls, wall_id: int) -> db.Model:
        return cls.query.filter_by(wall_id=wall_id).order_by(cls.id).all()


class Processing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer)
    month = db.Column(db.String(64))
    done = db.Column(db.String(32))
    wall_id = db.Column(db.Integer, db.ForeignKey("wall.id", ondelete="CASCADE"))

    @staticmethod
    def get_header() -> List:
        return [
            "Year",
            "Month",
            "Done",
        ]

    def calculate_rest_attributes(self) -> None:
        pass

    @classmethod
    def get_items_by_wall_id(cls, wall_id: int) -> db.Model:
        return cls.query.filter_by(wall_id=wall_id).order_by(cls.id).all()


class Wall(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    object = db.Column(db.String(64))
    level = db.Column(db.String(64))
    localization = db.Column(db.String(128))
    brick_type = db.Column(db.String(64))
    wall_width = db.Column(db.Integer)
    wall_length = db.Column(db.String(32))
    floor_ord = db.Column(db.String(32))
    ceiling_ord = db.Column(db.String(32))
    wall_height = db.Column(db.String(32))
    gross_wall_area = db.Column(db.String(32))
    wall_area_to_survey = db.Column(db.String(32))
    wall_area_to_sale = db.Column(db.String(32))
    left_to_sale = db.Column(db.String(32))
    holes = db.relationship(
        "Hole",
        backref="wall",
        lazy="dynamic",
        cascade="all, delete",
        passive_deletes=True,
    )
    processing = db.relationship(
        "Processing",
        backref="wall",
        lazy="dynamic",
        cascade="all, delete",
        passive_deletes=True,
    )
    # investment_id = db.Column(db.Integer, db.ForeignKey("investment.id"))

    @staticmethod
    def get_header() -> List:
        return [
            "Id",
            "Object",
            "Level",
            "Localization",
            "Brick type",
            "Wall width",
            "Wall length",
            "Floor ordinate",
            "Ceiling ordinate",
            "Wall height",
            "Gross wall area",
            "Wall area to survey",
            "Wall area to sale",
            "Left to sale",
        ]

    @classmethod
    def add_wall(cls, **kwargs) -> None:
        item = cls.create_item(cls, **kwargs)
        db.session.add(item)
        db.session.commit()

    @classmethod
    def add_hole(cls, wall_id: int, **kwargs) -> None:
        hole = cls.create_item(Hole, **kwargs)
        wall = cls.query.filter_by(id=wall_id).first()
        if wall:
            wall.holes.append(hole)
            wall.calculate_areas()
            wall.calculate_left_to_sale()
            db.session.add(wall)
            db.session.commit()

    @classmethod
    def add_processing(cls, wall_id: int, **kwargs) -> None:
        processing = cls.create_item(Processing, **kwargs)
        wall = cls.query.filter_by(id=wall_id).first()
        if wall:
            wall.processing.append(processing)
            wall.calculate_areas()
            wall.calculate_left_to_sale()
            db.session.add(wall)
            db.session.commit()

    @classmethod
    def edit_wall(cls, wall_id: int, **kwargs) -> None:
        wall = cls.query.filter_by(id=wall_id).first()
        if wall:
            cls.update_item(wall, **kwargs)
            db.session.add(wall)
            db.session.commit()

    @classmethod
    def edit_hole(cls, model_id: int, **kwargs) -> None:
        wall = (
            cls.query.join(Hole, Hole.wall_id == cls.id)
            .filter(Hole.id == model_id)
            .first()
        )
        if wall:
            cls.update_item(wall.holes[0], **kwargs)
            wall.calculate_areas()
            wall.calculate_left_to_sale()
            db.session.add(wall)
            db.session.commit()

    @classmethod
    def edit_processing(cls, model_id: int, **kwargs) -> None:
        wall = (
            cls.query.join(Processing, Processing.wall_id == cls.id)
            .filter(Processing.id == model_id)
            .first()
        )
        if wall:
            cls.update_item(wall.processing[0], **kwargs)
            wall.calculate_areas()
            wall.calculate_left_to_sale()
            db.session.add(wall)
            db.session.commit()

    @classmethod
    def delete_wall(cls, wall_id: int, **kwargs) -> None:
        # TODO finish
        pass

    @classmethod
    def delete_hole(cls, wall_id: int, model_id: int, **kwargs) -> None:
        # TODO finish
        pass

    @classmethod
    def delete_processing(cls, wall_id: int, model_id: int, **kwargs) -> None:
        # TODO finish
        pass

    @classmethod
    def create_item(cls, model: db.Model, **kwargs) -> db.Model:
        item = model()
        cls.update_item(item, **kwargs)
        return item

    @staticmethod
    def update_item(item: db.Model, **kwargs) -> db.Model:
        for attr, val in kwargs.items():
            item.__setattr__(attr, val)
        item.calculate_rest_attributes()
        return item

    def calculate_rest_attributes(self) -> None:
        wall_height = frac(self.ceiling_ord) - frac(self.floor_ord)
        gross_wall_area = frac(self.wall_length) * wall_height
        self.wall_height = float(wall_height)
        self.gross_wall_area = float(gross_wall_area)
        self.calculate_areas()
        self.calculate_left_to_sale()

    def calculate_areas(self) -> None:
        wall_area_to_survey = frac(self.gross_wall_area)
        wall_area_to_sale = frac(self.gross_wall_area)
        for hole in self.holes:
            wall_area_to_survey -= frac(hole.total_area)
            if not hole.below_3m2:
                wall_area_to_sale -= frac(hole.total_area) - frac(1)
        self.wall_area_to_survey = float(wall_area_to_survey)
        self.wall_area_to_sale = float(wall_area_to_sale)

    def calculate_left_to_sale(self):
        left_to_sale = frac(1)
        for item in self.processing:
            left_to_sale -= frac(item.done)
        if left_to_sale >= 0:
            self.left_to_sale = float(left_to_sale)
        else:
            self.left_to_sale = 0

    @classmethod
    def get_all_items(cls) -> db.Model:
        # return cls.query.filter_by(investment_id=investment_id)
        return cls.query.order_by(cls.id).all()

    def __repr__(self) -> str:
        return "<Wall(id=%s)>" % (self.id,)
