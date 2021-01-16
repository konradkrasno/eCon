from time import sleep
from app import create_celery_app

celery = create_celery_app()


@celery.task
def add(x, y):
    return x + y


@celery.task
def long_task(seconds: int):
    for i in range(seconds):
        print(i)
        sleep(1)
