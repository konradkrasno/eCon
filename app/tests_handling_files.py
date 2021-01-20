from flask import request
from app.handling_files import read_csv_file, read_csv_files, get_current_and_prev_path
from app.conftest import contexts_required


@contexts_required
def test_read_file():
    file = read_csv_file("test/walls.csv")
    assert type(file) == list


@contexts_required
def test_read_files():
    files = read_csv_files("test")
    for file in files:
        assert type(file) == list


def test_get_current_and_prev_path(app_and_db):
    assert (
        get_current_and_prev_path() == "econ/app/static/files/1/1"
    ), "econ/app/static/files/1/1"
