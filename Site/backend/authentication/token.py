import secrets
from time import time

from fastapi import Response
from sessions import db

TOKEN_LIFETIME = 60 * 60 * 24 * 7


async def get_session(session_id: str) -> dict | None:
    try:
        session_info = await db.holy_site.sessions.find_one({"session_id": session_id})
        if not session_info:
            return None
        return session_info
    except Exception:
        return None


async def create_session(user_id: str) -> str:
    session_id = str(secrets.token_hex(32))
    while (
        await db.holy_site.sessions.find_one({"session_id": session_id})
    ) is not None:
        session_id = str(secrets.token_hex(32))
    await db.holy_site.sessions.insert_one(
        {
            "session_id": session_id,
            "created": time(),
            "refresh": time() + TOKEN_LIFETIME / 2,
            "expires": time() + TOKEN_LIFETIME,
            "user_id": user_id,
        }
    )
    return session_id


async def verify_session(session_id: str):
    session_info = await get_session(session_id)

    if session_info is None:
        return None

    if time() >= session_info["expires"]:
        pass
    elif time() >= session_info["refresh"]:
        pass

    return True


def set_token_cookie(response: Response, session_id: str):
    response.set_cookie(
        "session",
        session_id,
        expires=TOKEN_LIFETIME,
        samesite="strict",
        domain="localhost",
        secure=True,
    )
