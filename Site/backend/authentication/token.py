import secrets
from time import time

from fastapi import Response
from sessions import db

TOKEN_LIFETIME = 60 * 60 * 24 * 7


async def verify_token(session_id: str):
    try:
        session_info = await db.holy_site.sessions.find_one({"session_id": session_id})
        if not session_info:
            return False
        return True
    except Exception:
        return False


async def create_session(user_id: str):
    session_id = str(secrets.token_hex(32))
    while (
        await db.holy_site.sessions.find_one({"session_id": session_id})
    ) is not None:
        session_id = str(secrets.token_hex(32))
    await db.holy_site.sessions.insert_one(
        {
            "session_id": session_id,
            "secret": secret,
            "expires": time() + TOKEN_LIFETIME,
            "user_id": user_id,
        }
    )
    return encoded_jwt


async def verify_session(encoded_jwt: str):
    session_info = await verify_token(encoded_jwt)
    if session_info is False:
        return None
    too_old = time() >= session_info["expires"]
    can_be_updated = time() <= (session_info["expires"] + (TOKEN_LIFETIME / 2))
    if too_old and can_be_updated:
        print("Updating token")
        return await create_session(session_info["user_id"])
    elif too_old and not can_be_updated:
        print("Token is too old, can't update")
        return None
    print("Token is up to date")
    return True


def set_token_cookie(response: Response, encoded_jwt: str):
    response.set_cookie(
        "token",
        encoded_jwt,
        expires=TOKEN_LIFETIME * 1.5,
        samesite="strict",
        domain="localhost",
        secure=True,
    )
