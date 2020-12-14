import pytest

from app import app, db
from config import config
from app.models import User, Investment, Hole, Processing, Wall
from sqlalchemy.engine import Engine

config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"


def drop_everything(engine: Engine):
    # from https://github.com/pallets/flask-sqlalchemy/issues/722
    from sqlalchemy.engine.reflection import Inspector
    from sqlalchemy.schema import (
        DropConstraint,
        DropTable,
        MetaData,
        Table,
        ForeignKeyConstraint,
    )

    con = engine.connect()
    trans = con.begin()
    inspector = Inspector.from_engine(db.engine)

    meta = MetaData()
    tables = []
    all_fkeys = []

    for table_name in inspector.get_table_names():
        fkeys = []
        for fkey in inspector.get_foreign_keys(table_name):
            if not fkey["name"]:
                continue
            fkeys.append(ForeignKeyConstraint((), (), name=fkey["name"]))
        tables.append(Table(table_name, meta, *fkeys))
        all_fkeys.extend(fkeys)

    for fkey in all_fkeys:
        con.execute(DropConstraint(fkey))

    for table in tables:
        con.execute(DropTable(table))

    trans.commit()


class TestModels:
    @classmethod
    def setup_class(cls):
        db.create_all()

    @classmethod
    def teardown_class(cls):
        db.session.remove()
        drop_everything(db.engine)

    def test_masonry_registry(self):
        kwargs = {
            "object": "K",
            "level": 2,
            "localization": "O/5",
            "brick_type": "YTONG",
            "wall_width": 24,
            "wall_length": 10.5,
            "floor_ord": 0,
            "ceiling_ord": 3.10,
            "hole_width": 1.5,
            "hole_height": 2.15,
            "holes_amount": 2,
        }
        Wall.add_item(**kwargs)
        assert Wall.get_all_items()
