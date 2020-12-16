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

    @classmethod
    def create_item(cls, **kwargs) -> db.Model:
        item = cls(
            width=kwargs["hole_width"],
            height=kwargs["hole_height"],
            amount=kwargs["holes_amount"],
        )
        item.calculate_rest_attributes()
        return item

    def calculate_rest_attributes(self):
        area = frac(self.width) * frac(self.height)
        total_area = area * frac(self.amount)
        self.area = float(area)
        self.total_area = float(total_area)
        self.below_3m2 = True if self.area < frac(3) else False

    def update_item(self, **kwargs):
        pass

    def delete_item(self, **kwargs):
        pass

    @classmethod
    def get_all_items(cls, wall_id: int) -> db.Model:
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

    @classmethod
    def create_item(cls, **kwargs) -> db.Model:
        item = cls(
            year=kwargs["year"],
            month=kwargs["month"],
            done=kwargs["done"],
        )
        return item

    def update_item(self, **kwargs):
        pass

    def delete_item(self, **kwargs):
        pass

    @classmethod
    def get_all_items(cls, wall_id: int) -> db.Model:
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
    def add_item(cls, **kwargs) -> None:
        item = cls(
            object=kwargs["object"],
            level=kwargs["level"],
            localization=kwargs["localization"],
            brick_type=kwargs["brick_type"],
            wall_width=kwargs["wall_width"],
            wall_length=kwargs["wall_length"],
            floor_ord=kwargs["floor_ord"],
            ceiling_ord=kwargs["ceiling_ord"],
        )
        item.calculate_rest_attributes()
        db.session.add(item)
        db.session.commit()

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

    def update_item(self, **kwargs):
        pass

    def delete_item(self, **kwargs):
        pass

    @classmethod
    def add_hole(cls, _id: int, **kwargs) -> None:
        hole = Hole.create_item(**kwargs)
        item = cls.query.filter_by(id=_id).first()
        if item:
            item.holes.append(hole)
            item.calculate_areas()
            item.calculate_left_to_sale()
            db.session.add(item)
            db.session.commit()

    @classmethod
    def add_processing(cls, _id: int, **kwargs) -> None:
        processing = Processing.create_item(**kwargs)
        item = cls.query.filter_by(id=_id).first()
        if item:
            item.processing.append(processing)
            item.calculate_areas()
            item.calculate_left_to_sale()
            db.session.add(item)
            db.session.commit()

    @classmethod
    def edit_model(cls, _id: int, model: str, **kwargs) -> None:
        item = cls.query.filter_by(id=_id).first()
        if item:
            item.__getattribute__(item, model).update_item(**kwargs)
            item.calculate_areas()
            item.calculate_left_to_sale()
            db.session.add(item)
            db.session.commit()

    @classmethod
    def get_all_items(cls) -> db.Model:
        # return cls.query.filter_by(investment_id=investment_id)
        return cls.query.order_by(cls.id).all()

    def __repr__(self) -> str:
        return "<Wall(id=%s)>" % (self.id,)
