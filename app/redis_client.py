from typing import *

import redis
import json


def create_notification(worker_id: int, n_type: str, description: str) -> Dict:
    return {
        "worker_id": worker_id,
        "n_type": n_type,
        "description": description
    }


def add_notification(r: redis.Redis, notification: Dict) -> None:
    worker_id = notification.get("worker_id")
    r.lpush(f"notifications:{worker_id}", json.dumps(notification))


def get_notification(r: redis.Redis, worker_id: int) -> Dict:
    try:
        _, notification = r.blpop(f"notifications:{worker_id}", timeout=1)
    except TypeError:
        notification = b"{}"
    return json.loads(notification)
