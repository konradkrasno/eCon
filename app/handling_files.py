from typing import *

import os, glob, shutil
import pandas as pd
from config import BASE_DIR, config
from flask import g
from flask_login import current_user


def get_temp_path() -> str:
    return os.path.join(BASE_DIR, config["UPLOAD_FOLDER"], "/temp")


def get_user_path(user_id: int, invest_id: int, path: str = "") -> str:
    return os.path.join(BASE_DIR, config["UPLOAD_FOLDER"], str(user_id), str(invest_id), path)


def read_csv_file(filename: str) -> List:
    temp_path = get_temp_path()
    file_path = os.path.join(temp_path, filename)
    return pd.read_csv(file_path, sep=";").to_dict(orient="records")


def read_csv_files(files_dir: str = "") -> Iterator:
    temp_path = get_temp_path()
    files_dir = os.path.join(temp_path, files_dir)
    files_path = files_dir + "/*.csv"
    files = glob.glob(files_path)
    for file in files:
        yield pd.read_csv(file, sep=";").to_dict(orient="records")


def create_new_folder(folder_path: str, folder_name: str) -> None:
    os.makedirs(os.path.join(folder_path, folder_name))


def save_file(file, filename: str, temp: bool = False, catalog: str = "") -> None:
    if not current_user.is_authenticated or g.current_invest.id is None:
        return
    if temp:
        file_dir = get_temp_path()
    else:
        file_dir = get_user_path(current_user.id, g.current_invest.id, catalog)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    file_path = os.path.join(file_dir, filename)
    if os.path.exists(file_path):
        raise FileExistsError
    file.save(file_path)


def remove(path: str) -> None:
    if os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=True)
    else:
        try:
            os.remove(path)
        except FileNotFoundError:
            pass


def handle_file(filename: str, model: str, Wall) -> List:
    messages = []
    if model == "walls":
        messages = Wall.upload_walls(g.current_invest.id, filename)
    elif model == "holes":
        messages = Wall.upload_holes(g.current_invest.id, filename)
    elif model == "processing":
        messages = Wall.upload_processing(g.current_invest.id, filename)
    elif model == "new_file":
        return ["New file uploaded successfully."]
    temp_path = get_temp_path()
    file_path = os.path.join(temp_path, filename)
    remove(file_path)
    return messages
