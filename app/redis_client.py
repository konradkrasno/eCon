import json
from typing import *

import redis

from app.app_tasks import tasks


def create_notification(worker_id: int, n_type: str, description: str) -> Dict:
    return {"worker_id": worker_id, "n_type": n_type, "description": description}


def add_notification(r: redis.Redis, notification: Dict) -> None:
    worker_id = notification.get("worker_id")
    r.lpush(f"notifications:{worker_id}", json.dumps(notification))


def get_notification(r: redis.Redis, worker_id: int) -> Dict:
    try:
        _, notification = r.blpop(f"notifications:{worker_id}", timeout=1)
    except TypeError:
        notification = b"{}"
    return json.loads(notification)


def populate_buffer(r: redis.Redis) -> None:
    fake_names = [
        "Niels Bohr",
        "Nicola Tesla",
        "Isaac Newton",
        "Albert Einstein",
        "Max Planck",
    ]
    for name in fake_names:
        r.lpush(f"fake_names", name)


def get_fake_name_from_buffer(r: redis.Redis) -> str:
    tasks.add_fake_name_to_buffer.delay()
    _, name = r.brpop(f"fake_names")
    return name.decode("utf-8")
