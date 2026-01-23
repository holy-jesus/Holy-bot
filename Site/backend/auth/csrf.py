import os
import secrets
from time import time
from datetime import timedelta

import valkey.asyncio as valkey

CSRF_TOKEN_LIFETIME = timedelta(
    minutes=int(os.getenv("CSRF_TOKEN_LIFETIME_MINUTES", "5"))
)
CSRF_MINIMUM_TIME_SINCE_ISSUE = timedelta(
    seconds=int(os.getenv("CSRF_MINIMUM_TIME_SINCE_ISSUE_SECONDS", "5"))
)
CSRF_RATE_LIMIT_WINDOW = timedelta(
    minutes=int(os.getenv("CSRF_RATE_LIMIT_WINDOW_MINUTES", "1"))
)
CSRF_RATE_LIMIT_MAX = int(os.getenv("CSRF_RATE_LIMIT_MAX", "5"))


async def create_csrf_token(ip_address: str, vk: valkey.Valkey) -> str:
    ratelimit_key = f"csrf:rl:{ip_address}"

    current = await vk.incr(ratelimit_key)
    if current == 1:
        await vk.expire(ratelimit_key, CSRF_RATE_LIMIT_WINDOW.seconds)

    if current > CSRF_RATE_LIMIT_MAX:
        raise RuntimeError("CSRF rate limit exceeded")

    csrf = secrets.token_urlsafe(32)
    now = time()

    await vk.set(
        name=f"csrf:{csrf}",
        value=now,
        ex=CSRF_TOKEN_LIFETIME.seconds,
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
