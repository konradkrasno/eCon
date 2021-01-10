from typing import *

from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property
from fractions import Fraction as frac
from app import db, login
from app.validators import (
    check_field_exists,
    validate_walls,
    validate_holes,
    validate_processing,
    validate_done_attr_while_adding,
    validate_done_attr_while_editing,
)
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from wtforms.validators import ValidationError
from app.loading_csv import read_csv_file


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    is_active = db.Column(db.Boolean())
    current_invest_id = db.Column(db.Integer())
    workers = db.relationship(
        "Worker",
        backref="users",
        lazy="dynamic",
        cascade="all, delete",
        passive_deletes=True,
    )

    def __init__(self, username: str, email: str, password: str):
        self.username = username
        self.email = email
        self.set_password(password)
        self.is_active = False

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @classmethod
    def get_user(cls, id: int) -> db.Model:
        if id:
            return cls.query.get(id)

    @classmethod
    def get_investments(cls, user_id: int) -> List:
        """ Returns list of investments which the user is the worker in it. """

        return (
            Investment.query.join(Worker, Worker.investment_id == Investment.id)
            .filter_by(user_id=user_id)
            .all()
        )

    @staticmethod
    def check_admins(user_id: int) -> Tuple[List, List]:
        """Returns list of investments which the user is the lonely admin
        and other workers belong to those investments."""

        projects = []
        empty_projects = []
        investments = User.get_investments(user_id=user_id)
        for invest in investments:
            if len(invest.workers.all()) < 2:
                empty_projects.append(invest)
            elif Investment.get_num_of_admins(invest.id) == 1:
                if Worker.is_admin(user_id=user_id, investment_id=invest.id):
                    projects.append(invest)
        return projects, empty_projects

    @staticmethod
    def get_workers(user_id: int) -> List:
        """ Returns list of workers, which the user is. """

        return Worker.query.filter_by(user_id=user_id).all()

    def __repr__(self) -> str:
        return "<User(username=%s)>" % (self.username,)


@login.user_loader
def load_user(id: str) -> User:
    return User.query.get(int(id))


class Worker(db.Model):
    __tablename__ = "workers"

    id = db.Column(db.Integer, primary_key=True)
    position = db.Column(db.String(128))
    admin = db.Column(db.Boolean())
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"))
    investment_id = db.Column(
        db.Integer, db.ForeignKey("investments.id", ondelete="CASCADE")
    )
    deputed_tasks = db.relationship(
        "Task",
        primaryjoin="(Worker.id == Task.orderer_id)",
        lazy="dynamic",
        cascade="all, delete",
        passive_deletes=True,
    )
    tasks_to_execution = db.relationship(
        "Task",
        primaryjoin="(Worker.id == Task.executor_id)",
        lazy="dynamic",
        cascade="all, delete",
        passive_deletes=True,
    )

    @classmethod
    def get_by_username(cls, invest_id: int, username: str) -> db.Model:
        return (
            cls.query.filter_by(investment_id=invest_id)
            .join(User, User.id == cls.user_id)
            .filter_by(username=username)
            .first()
        )

    @classmethod
    def belongs_to_investment(cls, email: str, investment_id: int) -> bool:
        return (
            cls.query.filter_by(investment_id=investment_id)
            .join(User, User.id == cls.user_id)
            .filter_by(email=email)
            .first()
            is not None
        )

    @classmethod
    def is_admin(cls, user_id: int, investment_id: int) -> bool:
        worker = cls.query.filter_by(
            investment_id=investment_id, user_id=user_id
        ).first()
        if worker:
            return worker.admin
        return False

    @classmethod
    def get_team(cls, investment_id: int) -> List:
        return cls.query.filter_by(investment_id=investment_id).order_by("id").all()


class Investment(db.Model):
    __tablename__ = "investments"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    description = db.Column(db.Text())
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    workers = db.relationship(
        "Worker",
        backref="investments",
        lazy="dynamic",
        cascade="all, delete",
        passive_deletes=True,
    )
    tasks = db.relationship(
        "Task",
        backref="investments",
        lazy="dynamic",
        cascade="all, delete",
        passive_deletes=True,
    )
    masonry_registry = db.relationship(
        "Wall",
        backref="investments",
        lazy="dynamic",
        cascade="all, delete",
        passive_deletes=True,
    )

    @classmethod
    def get_by_user_id(cls, user_id: int) -> db.Model:
        return (
            cls.query.join(Worker, Worker.investment_id == Investment.id)
            .order_by(cls.created_at.desc())
            .filter_by(user_id=user_id)
            .all()
        )

    @classmethod
    def get_current_invest(cls, user: User) -> db.Model:
        investment = (
            Investment.query.join(Worker, Worker.investment_id == Investment.id)
            .filter_by(user_id=user.id, investment_id=user.current_invest_id)
            .first()
        )
        if investment:
            return investment
        return Investment()

    @staticmethod
    def get_num_of_admins(investment_id: int) -> int:
        return len(
            Worker.query.filter_by(investment_id=investment_id, admin=True).all()
        )

    def __repr__(self) -> str:
        return "<Investment(name=%s)>" % (self.name,)


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    deadline = db.Column(db.Date)
    priority = db.Column(db.Integer)
    orderer_id = db.Column(db.Integer, db.ForeignKey("workers.id", ondelete="CASCADE"))
    executor_id = db.Column(db.Integer, db.ForeignKey("workers.id", ondelete="CASCADE"))
    orderer = db.relationship("Worker", foreign_keys=[orderer_id])
    executor = db.relationship("Worker", foreign_keys=[executor_id])
    progress = db.Column(db.Integer)
    investment_id = db.Column(
        db.Integer, db.ForeignKey("investments.id", ondelete="CASCADE")
    )

    @classmethod
    def get_in_progress(cls, invest_id: int) -> List:
        return (
            Task.query.filter_by(investment_id=invest_id)
            .filter(cls.progress != 100)
            .order_by(Task.deadline)
            .order_by(Task.priority.desc())
            .all()
        )

    @classmethod
    def get_realized(cls, invest_id: int) -> List:
        return (
            Task.query.filter_by(investment_id=invest_id)
            .filter(cls.progress == 100)
            .order_by(Task.deadline)
            .order_by(Task.priority.desc())
            .all()
        )

    def __repr__(self) -> str:
        return "<Task(description=%s)>" % (self.description,)


class Hole(db.Model):
    __tablename__ = "holes"

    id = db.Column(db.Integer, primary_key=True)
    width = db.Column(db.Float(precision=2))
    height = db.Column(db.Float(precision=2))
    amount = db.Column(db.Integer)
    wall_id = db.Column(db.Integer, db.ForeignKey("walls.id", ondelete="CASCADE"))

    @hybrid_property
    def area(self):
        return round(float(self.__compute_area()), 2)

    @hybrid_property
    def total_area(self):
        return round(float(self.__compute_total_area()), 2)

    @hybrid_property
    def below_3m2(self):
        return self.__compute_below_3m2()

    def __compute_area(self) -> frac:
        return frac(str(self.width)) * frac(str(self.height))

    def __compute_total_area(self) -> frac:
        area = self.__compute_area()
        return area * frac(str(self.amount))

    def __compute_below_3m2(self) -> bool:
        return True if self.area < 3 else False

    @classmethod
    def create_item(cls, **kwargs) -> db.Model:
        return cls(
            width=kwargs.get("width"),
            height=kwargs.get("height"),
            amount=kwargs.get("amount"),
            wall_id=kwargs.get("wall_id"),
        )

    @classmethod
    def get_items_by_wall_id(cls, wall_id: int) -> db.Model:
        return cls.query.filter_by(wall_id=wall_id).order_by(cls.id).all()


class Processing(db.Model):
    __tablename__ = "processing"

    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer)
    month = db.Column(db.String(64))
    _done = db.Column(db.Float(precision=2))
    wall_id = db.Column(db.Integer, db.ForeignKey("walls.id", ondelete="CASCADE"))

    @hybrid_property
    def done(self):
        return self._done

    @done.setter
    def done(self, value):
        if frac(str(value)) < frac("0"):
            raise ValueError("Value: done cannot be less then 1!")
        if frac(str(value)) > frac("1"):
            raise ValueError("Value: done cannot be greater then 1!")
        self._done = value

    @classmethod
    def create_item(cls, **kwargs) -> db.Model:
        return cls(
            year=kwargs.get("year"),
            month=kwargs.get("month"),
            done=kwargs.get("done"),
            wall_id=kwargs.get("wall_id"),
        )

    @classmethod
    def get_items_by_wall_id(cls, wall_id: int) -> db.Model:
        return cls.query.filter_by(wall_id=wall_id).order_by(cls.id).all()


class Wall(db.Model):
    __tablename__ = "walls"

    id = db.Column(db.Integer, primary_key=True)
    local_id = db.Column(db.Integer)
    sector = db.Column(db.String(64))
    level = db.Column(db.String(64))
    localization = db.Column(db.String(128))
    brick_type = db.Column(db.String(64))
    wall_width = db.Column(db.Integer)
    wall_length = db.Column(db.Float(precision=2))
    floor_ord = db.Column(db.Float(precision=2))
    ceiling_ord = db.Column(db.Float(precision=2))
    holes = db.relationship(
        "Hole",
        backref="walls",
        lazy="dynamic",
        cascade="all, delete",
        passive_deletes=True,
    )
    processing = db.relationship(
        "Processing",
        backref="walls",
        lazy="dynamic",
        cascade="all, delete",
        passive_deletes=True,
    )
    investment_id = db.Column(
        db.Integer, db.ForeignKey("investments.id", ondelete="CASCADE")
    )

    @hybrid_property
    def wall_height(self):
        return round(float(self.__compute_wall_height()), 2)

    @hybrid_property
    def gross_wall_area(self):
        return round(float(self.__compute_gross_wall_area()), 2)

    @hybrid_property
    def wall_area_to_survey(self):
        return round(float(self.__compute_wall_area_to_survey()), 2)

    @hybrid_property
    def wall_area_to_sale(self):
        return round(float(self.__compute_wall_area_to_sale()), 2)

    @hybrid_property
    def left_to_sale(self):
        return round(float(self.__compute_left_to_sale()), 2)

    def __compute_wall_height(self) -> frac:
        return frac(str(self.ceiling_ord)) - frac(str(self.floor_ord))

    def __compute_gross_wall_area(self) -> frac:
        wall_height = self.__compute_wall_height()
        return frac(str(self.wall_length)) * wall_height

    def __compute_wall_area_to_survey(self) -> frac:
        wall_area_to_survey = self.__compute_gross_wall_area()
        for hole in self.holes:
            wall_area_to_survey -= frac(str(hole.total_area))
        return wall_area_to_survey

    def __compute_wall_area_to_sale(self) -> frac:
        wall_area_to_sale = self.__compute_gross_wall_area()
        for hole in self.holes:
            if not hole.below_3m2:
                wall_area_to_sale -= frac(str(hole.total_area)) - frac(str(hole.amount))
        return wall_area_to_sale

    def __compute_left_to_sale(self) -> frac:
        left_to_sale = frac("1")
        for item in self.processing.order_by(Processing.id):
            if left_to_sale < frac(str(item.done)):
                return frac("0.0")
            left_to_sale -= frac(str(item.done))
        return left_to_sale

    @classmethod
    def create_item(cls, invest_id: int, **kwargs) -> db.Model:
        return cls(
            local_id=kwargs.get("local_id"),
            sector=kwargs.get("sector"),
            level=kwargs.get("level"),
            localization=kwargs.get("localization"),
            brick_type=kwargs.get("brick_type"),
            wall_width=kwargs.get("wall_width"),
            wall_length=kwargs.get("wall_length"),
            floor_ord=kwargs.get("floor_ord"),
            ceiling_ord=kwargs.get("ceiling_ord"),
            investment_id=invest_id,
        )

    @classmethod
    def add_wall(cls, invest_id: int, **kwargs) -> None:
        wall = cls.create_item(invest_id, **kwargs)
        db.session.add(wall)
        db.session.commit()

    @classmethod
    def add_hole(cls, wall_id: int, **kwargs) -> None:
        wall = cls.query.filter_by(id=wall_id).first()
        if wall:
            hole = Hole.create_item(**kwargs)
            wall.holes.append(hole)
            db.session.add(wall)
            db.session.commit()

    @classmethod
    def add_processing(cls, wall_id: int, **kwargs) -> None:
        wall = cls.query.filter_by(id=wall_id).first()
        if wall:
            kwargs = validate_done_attr_while_adding(wall, kwargs)
            processing = Processing.create_item(**kwargs)
            wall.processing.append(processing)
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
                kwargs = validate_done_attr_while_editing(wall, processing, kwargs)
                cls.update_item(processing, **kwargs)
                db.session.add(wall)
                db.session.commit()

    @staticmethod
    def update_item(item: db.Model, **kwargs) -> db.Model:
        kwargs.pop("id", None)
        for attr, val in kwargs.items():
            item.__setattr__(attr, val)
        return item

    @classmethod
    def delete_wall(cls, wall_id: int) -> None:
        cls.query.filter_by(id=wall_id).delete()
        db.session.commit()

    @staticmethod
    def delete_hole(model_id: int) -> None:
        Hole.query.filter_by(id=model_id).delete()
        db.session.commit()

    @staticmethod
    def delete_processing(model_id: int) -> None:
        Processing.query.filter_by(id=model_id).delete()
        db.session.commit()

    @classmethod
    def upload_walls(cls, invest_id: int, filename: str) -> List:
        success = 0
        failures = []
        try:
            file = read_csv_file(filename)
        except Exception as e:
            return [
                'An error occurred: "{}", while loading file: "{}"'.format(e, filename)
            ]
        else:
            for data in file:
                local_id = check_field_exists(data, "local_id")
                if local_id:
                    try:
                        data = validate_walls(data)
                    except ValidationError:
                        failures.append(local_id)
                    else:
                        wall = (
                            Wall.get_all_items(invest_id)
                            .filter_by(local_id=local_id)
                            .first()
                        )
                        if wall:
                            wall = Wall.update_item(wall, **data)
                        else:
                            wall = Wall.create_item(invest_id, **data)
                        db.session.add(wall)
                        try:
                            db.session.commit()
                        except Exception:
                            db.session.rollback()
                            failures.append(local_id)
                        else:
                            success += 1
            return cls.create_upload_messages(success, failures)

    @classmethod
    def upload_holes(cls, invest_id: int, filename: str) -> List:
        success = 0
        failures = []
        no_wall = []
        wall_ids = []
        try:
            file = read_csv_file(filename)
        except Exception as e:
            return [
                'An error occurred: "{}", while loading file: "{}"'.format(e, filename)
            ]
        else:
            for data in file:
                wall_local_id = check_field_exists(data, "wall_id")
                if wall_local_id:
                    wall = (
                        Wall.get_all_items(invest_id)
                        .filter_by(local_id=wall_local_id)
                        .first()
                    )
                    if wall:
                        # deleting all holes with particular wall_id before uploading from csv
                        if wall.id not in wall_ids:
                            Hole.query.filter_by(wall_id=wall.id).delete()
                            wall_ids.append(wall.id)
                        try:
                            data = validate_holes(data)
                        except ValidationError:
                            failures.append(wall_local_id)
                        else:
                            hole = Hole.create_item(**data)
                            wall.holes.append(hole)
                            db.session.add(wall)
                            try:
                                db.session.commit()
                            except Exception:
                                db.session.rollback()
                                failures.append(wall_local_id)
                            else:
                                success += 1
                    else:
                        no_wall.append(wall_local_id)
            return cls.create_upload_messages(success, failures, no_wall)

    @classmethod
    def upload_processing(cls, invest_id: int, filename: str) -> List:
        success = 0
        failures = []
        no_wall = []
        no_left = []
        wall_ids = []
        try:
            file = read_csv_file(filename)
        except Exception as e:
            return [
                'An error occurred: "{}", while loading file: "{}"'.format(e, filename)
            ]
        else:
            for data in file:
                wall_local_id = check_field_exists(data, "wall_id")
                if wall_local_id:
                    wall = (
                        Wall.get_all_items(invest_id)
                        .filter_by(local_id=wall_local_id)
                        .first()
                    )
                    if wall:
                        # deleting all processing with particular wall_id before uploading from csv
                        if wall.id not in wall_ids:
                            Processing.query.filter_by(wall_id=wall.id).delete()
                            wall_ids.append(wall.id)
                        if wall.left_to_sale == 0:
                            no_left.append(wall_local_id)
                            continue
                        try:
                            data = validate_processing(wall, data)
                        except ValidationError:
                            failures.append(wall_local_id)
                        else:
                            processing = Processing.create_item(**data)
                            wall.processing.append(processing)
                            db.session.add(wall)
                            try:
                                db.session.commit()
                            except Exception:
                                db.session.rollback()
                                failures.append(wall_local_id)
                            else:
                                success += 1
                    else:
                        no_wall.append(wall_local_id)
            return cls.create_upload_messages(success, failures, no_wall, no_left)

    @staticmethod
    def create_upload_messages(
        success: int, failures: List, no_wall: List = None, no_left=None
    ) -> List:
        messages = []
        messages.append("Uploaded {} items.".format(success))
        if failures:
            messages.append(
                "Items: {} not added because they has the wrong format.".format(
                    failures
                )
            )
        if no_wall:
            messages.append(
                "Items: {} not added because wall with specified id does not exist. Add wall first.".format(
                    no_wall
                )
            )
        if no_left:
            messages.append(
                "Items: {} not added because value of left_to_sale is 0.".format(
                    no_left
                )
            )
        return messages

    @classmethod
    def get_all_items(cls, invest_id: int) -> db.Model:
        return cls.query.filter_by(investment_id=invest_id)

    @classmethod
    def get_left_to_sale(cls, wall_id: int) -> float:
        wall = Wall.query.filter_by(id=wall_id).first()
        if wall:
            return wall.left_to_sale
        return 0

    def __repr__(self) -> str:
        return "<Wall(id=%s)>" % (self.id,)
