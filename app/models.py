from typing import *

from sqlalchemy.ext.hybrid import hybrid_property
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
    wall_id = db.Column(db.Integer, db.ForeignKey("wall.id", ondelete="CASCADE"))

    @hybrid_property
    def area(self):
        return float(self.__compute_area())

    @hybrid_property
    def total_area(self):
        return float(self.__compute_total_area())

    @hybrid_property
    def below_3m2(self):
        return self.__compute_below_3m2()

    def __compute_area(self) -> frac:
        return frac(self.width) * frac(self.height)

    def __compute_total_area(self) -> frac:
        area = self.__compute_area()
        return area * frac(self.amount)

    def __compute_below_3m2(self) -> bool:
        return True if self.area < 3 else False

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
    def get_items_by_wall_id(cls, wall_id: int) -> db.Model:
        return cls.query.filter_by(wall_id=wall_id).order_by(cls.id).all()


class Processing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer)
    month = db.Column(db.String(64))
    _done = db.Column(db.String(32))
    wall_id = db.Column(db.Integer, db.ForeignKey("wall.id", ondelete="CASCADE"))

    @hybrid_property
    def done(self):
        return str(self._done)

    @done.setter
    def done(self, value):
        if frac(str(value)) < frac("0"):
            raise ValueError("Value: done cannot be less then 1!")
        if frac(str(value)) > frac("1"):
            raise ValueError("Value: done cannot be greater then 1!")
        self._done = str(value)

    @staticmethod
    def get_header() -> List:
        return [
            "Year",
            "Month",
            "Done",
        ]

    @classmethod
    def get_items_by_wall_id(cls, wall_id: int) -> db.Model:
        return cls.query.filter_by(wall_id=wall_id).order_by(cls.id).all()


class Wall(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sector = db.Column(db.String(64))
    level = db.Column(db.String(64))
    localization = db.Column(db.String(128))
    brick_type = db.Column(db.String(64))
    wall_width = db.Column(db.Integer)
    wall_length = db.Column(db.String(32))
    floor_ord = db.Column(db.String(32))
    ceiling_ord = db.Column(db.String(32))
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

    @hybrid_property
    def wall_height(self):
        return float(self.__compute_wall_height())

    @hybrid_property
    def gross_wall_area(self):
        return float(self.__compute_gross_wall_area())

    @hybrid_property
    def wall_area_to_survey(self):
        return float(self.__compute_wall_area_to_survey())

    @hybrid_property
    def wall_area_to_sale(self):
        return float(self.__compute_wall_area_to_sale())

    @hybrid_property
    def left_to_sale(self):
        return float(self.__compute_left_to_sale())

    def __compute_wall_height(self) -> frac:
        return frac(self.ceiling_ord) - frac(self.floor_ord)

    def __compute_gross_wall_area(self) -> frac:
        wall_height = self.__compute_wall_height()
        return frac(self.wall_length) * wall_height

    def __compute_wall_area_to_survey(self) -> frac:
        wall_area_to_survey = self.__compute_gross_wall_area()
        for hole in self.holes:
            wall_area_to_survey -= frac(str(hole.total_area))
        return wall_area_to_survey

    def __compute_wall_area_to_sale(self) -> frac:
        wall_area_to_sale = self.__compute_gross_wall_area()
        for hole in self.holes:
            if not hole.below_3m2:
                wall_area_to_sale -= frac(str(hole.total_area)) - frac("1")
        return wall_area_to_sale

    def __compute_left_to_sale(self) -> frac:
        left_to_sale = frac("1")
        for item in self.processing.order_by(Processing.id):
            if left_to_sale < frac(str(item.done)):
                return frac("0.0")
            left_to_sale -= frac(str(item.done))
        return left_to_sale

    @staticmethod
    def get_header() -> List:
        return [
            "Id",
            "Sector",
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
        wall = cls.query.filter_by(id=wall_id).first()
        if wall:
            hole = cls.create_item(Hole, **kwargs)
            wall.holes.append(hole)
            db.session.add(wall)
            db.session.commit()

    @classmethod
    def add_processing(cls, wall_id: int, **kwargs) -> None:
        wall = cls.query.filter_by(id=wall_id).first()
        if wall:
            kwargs = cls.validate_done_attr_while_adding(wall, kwargs)
            processing = cls.create_item(Processing, **kwargs)
            wall.processing.append(processing)
            db.session.add(wall)
            db.session.commit()

    @staticmethod
    def validate_done_attr_while_adding(wall: db.Model, data: Dict) -> Dict:
        done = data.get("done")
        if done:
            if float(done) > 1:
                raise ValueError("Value: done cannot be greater then 1!")
            if float(wall.left_to_sale) < float(done):
                data["done"] = str(wall.left_to_sale)
        return data

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
            hole = wall.holes.filter_by(id=model_id).first()
            if hole:
                cls.update_item(hole, **kwargs)
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
            processing = wall.processing.filter_by(id=model_id).first()
            if processing:
                kwargs = cls.validate_done_attr_while_editing(wall, processing, kwargs)
                cls.update_item(processing, **kwargs)
                db.session.add(wall)
                db.session.commit()

    @staticmethod
    def validate_done_attr_while_editing(
        wall: db.Model, processing: db.Model, data: Dict
    ) -> Dict:
        done = data.get("done")
        if done:
            if float(done) > 1:
                raise ValueError("Value: done cannot be greater then 1!")
            left_to_sale = frac(str(wall.left_to_sale))
            left_to_sale += frac(str(processing.done))
            if float(left_to_sale) < float(done):
                data["done"] = str(float(left_to_sale))
        return data

    @classmethod
    def delete_wall(cls, wall_id: int) -> None:
        wall = Wall.query.filter_by(id=wall_id).first()
        db.session.delete(wall)
        db.session.commit()

    @classmethod
    def delete_hole(cls, model_id: int) -> None:
        hole = Hole.query.filter_by(id=model_id).first()
        db.session.delete(hole)
        db.session.commit()

    @classmethod
    def delete_processing(cls, model_id: int) -> None:
        processing = Processing.query.filter_by(id=model_id).first()
        db.session.delete(processing)
        db.session.commit()

    @classmethod
    def create_item(cls, model: db.Model, **kwargs) -> db.Model:
        item = model()
        cls.update_item(item, **kwargs)
        return item

    @staticmethod
    def update_item(item: db.Model, **kwargs) -> db.Model:
        for attr, val in kwargs.items():
            item.__setattr__(attr, val)
        return item

    @classmethod
    def get_all_items(cls) -> db.Model:
        # return cls.query.filter_by(investment_id=investment_id)
        return cls.query.order_by(cls.id).all()

    @classmethod
    def get_left_to_sale(cls, wall_id: int) -> float:
        wall = Wall.query.filter_by(id=wall_id).first()
        if wall:
            return wall.left_to_sale
        return 0

    def __repr__(self) -> str:
        return "<Wall(id=%s)>" % (self.id,)
