from typing import *

import os
import pandas as pd

from config import BASE_DIR


def get_file_path(file_dir: str) -> os.path:
    return os.path.join(BASE_DIR, file_dir)


def read_file(file_dir: str) -> List:
    return pd.read_csv(get_file_path(file_dir), sep=";").to_dict(orient="records")


def read_files(files: List) -> Iterator:
    for file in files:
        yield pd.read_csv(get_file_path(file), sep=";").to_dict(orient="records")
