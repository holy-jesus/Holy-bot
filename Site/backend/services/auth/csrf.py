import os
import secrets
from time import time
from datetime import timedelta

import valkey.asyncio as valkey
from Site.backend.services.ratelimit import ratelimit

CSRF_TOKEN_TTL = timedelta(
    minutes=int(os.getenv("CSRF_TOKEN_TTL_MINUTES", "5"))
)
CSRF_MINIMUM_TIME_SINCE_ISSUE = timedelta(
    seconds=int(os.getenv("CSRF_MINIMUM_TIME_SINCE_ISSUE_SECONDS", "5"))
)
CSRF_RATE_LIMIT_WINDOW = timedelta(
    minutes=int(os.getenv("CSRF_RATE_LIMIT_WINDOW_MINUTES", "1"))
)
CSRF_RATE_LIMIT_MAX = int(os.getenv("CSRF_RATE_LIMIT_MAX", "5"))


async def create_csrf_token(ip_address: str, vk: valkey.Valkey) -> str:
    is_ratelimited = await ratelimit(
        f"csrf:ratelimit:{ip_address}",
        CSRF_RATE_LIMIT_MAX,
        CSRF_RATE_LIMIT_WINDOW.seconds,
        vk,
    )

    if is_ratelimited:
        raise RuntimeError("CSRF rate limit exceeded")

    csrf = secrets.token_urlsafe(32)
    now = time()

    await vk.set(
        name=f"csrf:{csrf}",
        value=now,
        ex=CSRF_TOKEN_TTL.seconds,
    )

    return csrf


async def check_csrf_token(csrf: str, vk: valkey.Valkey) -> bool:
    key = f"csrf:{csrf}"

    timestamp = await vk.get(key)
    if timestamp is None:
        return False

    await vk.delete(key)

    age = time() - float(timestamp)
    return age >= CSRF_MINIMUM_TIME_SINCE_ISSUE.total_seconds()
