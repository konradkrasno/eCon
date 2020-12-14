from typing import *

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
    width = db.Column(db.Float)
    height = db.Column(db.Float)
    amount = db.Column(db.Integer)
    area = db.Column(db.Float)
    total_area = db.Column(db.Float)
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
        self.area = self.width * self.height
        self.total_area = self.area * self.amount
        self.below_3m2 = True if self.area < 3 else False

    def update_item(self, **kwargs):
        pass


class Processing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer)
    month = db.Column(db.String(64))
    done = db.Column(db.Float)
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


class Wall(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    object = db.Column(db.String(64))
    level = db.Column(db.String(64))
    localization = db.Column(db.String(128))
    brick_type = db.Column(db.String(64))
    wall_width = db.Column(db.Integer)
    wall_length = db.Column(db.Float)
    floor_ord = db.Column(db.Float)
    ceiling_ord = db.Column(db.Float)
    wall_height = db.Column(db.Float)
    gross_wall_area = db.Column(db.Float)
    wall_area_to_survey = db.Column(db.Float)
    wall_area_to_sale = db.Column(db.Float)
    left_to_sale = db.Column(db.Float)
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
        self.wall_height = self.ceiling_ord - self.floor_ord
        self.gross_wall_area = self.wall_length * self.wall_height
        self.calculate_areas()
        self.calculate_left_to_sale()

    def calculate_areas(self) -> None:
        self.wall_area_to_survey = self.gross_wall_area
        self.wall_area_to_sale = self.gross_wall_area
        for hole in self.holes:
            self.wall_area_to_survey -= hole.total_area
            if not hole.below_3m2:
                self.wall_area_to_sale -= hole.total_area + 1

    def calculate_left_to_sale(self):
        self.left_to_sale = 1
        for item in self.processing:
            self.left_to_sale -= item.done

    def update_item(self, **kwargs):
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
        return cls.query.all()

    def __repr__(self) -> str:
        return "<Wall(id=%s)>" % (self.id,)
