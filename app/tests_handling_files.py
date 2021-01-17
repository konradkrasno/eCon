from app.handling_files import read_csv_file, read_csv_files
from app.conftest import contexts_required


@contexts_required
def test_read_file():
    file = read_csv_file("test/walls.csv")
    assert type(file) == list


def test_read_files():
    files = read_csv_files("test")
    for file in files:
        assert type(file) == list
