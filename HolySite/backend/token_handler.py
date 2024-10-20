import secrets
from time import time

import jwt
from fastapi import Response

from sessions import db


LIFETIME = 86400


def create_token(session_id: str):
    secret = secrets.token_bytes(256)
    encoded_jwt = jwt.encode({"session_id": session_id}, secret, "HS256")
    return secret, encoded_jwt


async def verify_token(token: str):
    try:
        payload: dict = jwt.decode(token, options={"verify_signature": False})
        if len(payload.keys()) != 1 or "session_id" not in payload:
            return False
        session_id = payload["session_id"]
        if len(session_id) != 64:
            return False
        try:
            int(session_id, 16)
        except ValueError:
            return False
        session_info = await db.holy_site.sessions.find_one({"session_id": session_id})
        if not session_info:
            return False
        secret = session_info["secret"]
        try:
            jwt.decode(token, secret, algorithms=["HS256"])
            return session_info
        except jwt.DecodeError:
            return False
    except Exception:
        return False


async def create_session(user_id: str):
    session_id = str(secrets.token_hex(32))
    while (
        await db.holy_site.sessions.find_one({"session_id": session_id})
    ) is not None:
        session_id = str(secrets.token_hex(32))
    secret, encoded_jwt = create_token(session_id)
    await db.holy_site.sessions.insert_one(
        {
            "session_id": session_id,
            "secret": secret,
            "expires": time() + LIFETIME,
            "user_id": user_id,
        }
    )
    return encoded_jwt


async def verify_session(encoded_jwt: str):
    session_info = await verify_token(encoded_jwt)
    if session_info is False:
        return None
    too_old = time() >= session_info["expires"]
    can_be_updated = (session_info["expires"] + (LIFETIME / 2)) <= time()
    if too_old and can_be_updated:
        return await create_session(session_info["user_id"])
    elif too_old and not can_be_updated:
        return None
    return True

def set_token_cookie(response: Response, encoded_jwt: str):
    response.set_cookie(
        "token", encoded_jwt, secure=True, expires=LIFETIME * 1.5, samesite="strict"
    )