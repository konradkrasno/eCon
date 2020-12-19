from typing import *

import os, glob
import pandas as pd

from config import BASE_DIR, config


def read_csv_file(filename: str) -> List:
    file_path = os.path.join(BASE_DIR, config["UPLOAD_FOLDER"], filename)
    return pd.read_csv(file_path, sep=";").to_dict(orient="records")


def read_csv_files(files_dir: str = "") -> Iterator:
    files_dir = os.path.join(BASE_DIR, config["UPLOAD_FOLDER"], files_dir)
    files_path = files_dir + "*.csv"
    files = glob.glob(files_path)
    for file in files:
        yield pd.read_csv(file, sep=";").to_dict(orient="records")


def remove_file(filename: str):
    file_path = os.path.join(BASE_DIR, config["UPLOAD_FOLDER"], filename)
    os.remove(file_path)
