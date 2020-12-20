import pytest


from app.loading_csv import read_csv_file, read_csv_files


def test_read_file():
    file = read_csv_file("test/walls.csv")
    assert type(file) == list


def test_read_files():
    files = read_csv_files("test/")
    for file in files:
        assert type(file) == list