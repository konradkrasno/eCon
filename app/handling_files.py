from typing import *

import os
import glob
import shutil
import time
import pandas as pd

from config import BASE_DIR, config
from flask import flash, redirect, url_for, g, request
from flask_login import current_user


def allowed_file(filename: str) -> bool:
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in config["ALLOWED_EXTENSIONS"]
    )


def get_temp_path() -> str:
    return os.path.abspath(os.path.join(BASE_DIR, config["UPLOAD_FOLDER"], "temp"))


def get_user_path(user_id: int, invest_id: int, path: str = "") -> str:
    return os.path.abspath(
        os.path.join(
            BASE_DIR, config["UPLOAD_FOLDER"], str(user_id), str(invest_id), path
        )
    )


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


def handle_csv(filename: str, invest_id: int, model: str, Wall) -> List:
    messages = []
    if model == "walls":
        messages = Wall.upload_walls(invest_id, filename)
    elif model == "holes":
        messages = Wall.upload_holes(invest_id, filename)
    elif model == "processing":
        messages = Wall.upload_processing(invest_id, filename)
    temp_path = get_temp_path()
    file_path = os.path.abspath(os.path.join(temp_path, filename))
    remove(file_path)
    return messages


def create_new_folder(folder_path: str, folder_name: str) -> None:
    path = os.path.abspath(os.path.join(folder_path, folder_name))
    if not os.path.exists(path):
        os.makedirs(path)


def save_file(
    file,
    file_dir: str,
    filename: str,
    temp: bool = False,
) -> None:
    if temp:
        file_dir = get_temp_path()
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    file_path = os.path.abspath(os.path.join(file_dir, filename))
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


def get_metadata(paths: List) -> Tuple[List, List]:
    files = []
    folders = []
    for path in paths:
        item = {
            "name": os.path.basename(path),
            "created_at": time.ctime(os.path.getctime(path)),
            "last_modified": time.ctime(os.path.getmtime(path)),
        }
        if os.path.isdir(path):
            folders.append(item)
        else:
            files.append(item)
    return files, folders


def validate_path(path: str, user_path: str) -> str:
    path = os.path.abspath(path)
    if path.startswith(user_path):
        return path
    return user_path


def get_current_and_prev_path() -> Tuple[str, str]:
    user_path = get_user_path(current_user.id, g.current_invest.id)
    current_path = request.args.get("current_path")
    if not current_path:
        current_path = user_path
    catalog = request.args.get("catalog")
    if catalog:
        prev_path = current_path
        current_path = os.path.abspath(os.path.join(current_path, catalog))
    else:
        if current_path == user_path:
            prev_path = current_path
        else:
            prev_path = os.path.abspath(os.path.join(current_path, os.pardir))
    current_path = validate_path(current_path, user_path)
    prev_path = validate_path(prev_path, user_path)
    return current_path, prev_path
