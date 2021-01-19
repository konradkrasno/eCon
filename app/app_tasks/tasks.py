import os
import shutil

from app.app_tasks import create_celery_app
from time import sleep


celery = create_celery_app()


@celery.task
def add(x, y):
    return x + y


@celery.task
def long_task(seconds: int):
    for i in range(seconds):
        print(i)
        sleep(1)


@celery.task
def archive_and_save(path: str, catalog: str) -> None:
    catalog_path = os.path.join(path, catalog)
    shutil.make_archive(catalog_path, "zip", catalog_path)
