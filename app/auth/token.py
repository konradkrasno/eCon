from typing import *

import jwt
from time import time
from config import config


def get_confirmation_token(expires_in=600, **kwargs) -> bytes:
    return jwt.encode(
        {"conf_token": kwargs, "exp": time() + expires_in},
        config["SECRET_KEY"],
        algorithm="HS256",
    )


def verify_token(token: bytes) -> Dict:
    try:
        return jwt.decode(token, config["SECRET_KEY"], algorithms=["HS256"])[
            "conf_token"
        ]
    except Exception:
        return {}
