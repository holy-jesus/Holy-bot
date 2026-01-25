from .auth import auth

import secrets
from hashlib import sha256

import valkey.asyncio as valkey
from fastapi import Request, Response, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr

from Site.backend.deps import get_db_session
from Site.backend.services.auth.user import (
    get_user_by_id,
    get_user_by_username,
    get_user_by_email,
)
from Site.backend.services.auth.session import create_session, SESSION_LIFETIME
from Site.backend.services.email import send_login_code
from Site.backend.models import UserLoginWithPassword
from Site.backend.services.auth.cookie import set_session_cookie
from Site.backend.services.ratelimit import ratelimit
from Site.backend.services.auth.password import verify_password
import json

LIMIT = 3
WINDOW = 60
LOGIN_CODE_LIFETIME = 30 * 60


@auth.post("/login")
async def login_user(
    request: Request,
    response: Response,
    user: UserLoginWithPassword,
    db: AsyncSession = Depends(get_db_session),
):
    vk: valkey.Valkey = request.app.state.valkey
    is_host_ratelimited = await ratelimit(
        f"auth:login:ratelimit:{request.client.host}", LIMIT, WINDOW, vk
    )
    if is_host_ratelimited:
        raise HTTPException(status_code=429, detail="Too many requests")

    db_user = await get_user_by_username(user.username, db)
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    is_password_correct = db_user.password_hash is not None and verify_password(
        user.password, db_user.password_hash
    )

    if not is_password_correct:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    session = await create_session(db_user, db)

    set_session_cookie(response, session.id)

    return {"status": "ok", "user_id": str(db_user.id)}


@auth.post("/request-login-code")
async def request_login_code(
    request: Request,
    email: EmailStr,
    db: AsyncSession = Depends(get_db_session),
):
    vk: valkey.Valkey = request.app.state.valkey

    is_email_ratelimited = await ratelimit(
        f"auth:login_code:ratelimit:{email}", LIMIT, WINDOW, vk
    )
    is_host_ratelimited = await ratelimit(
        f"auth:login_code:ratelimit:{request.client.host}", LIMIT, WINDOW, vk
    )

    if is_email_ratelimited or is_host_ratelimited:
        raise HTTPException(
            status_code=429,
            detail="Too many requests",
        )

    db_user = await get_user_by_email(email, db)
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid email")

    verification_code = secrets.token_hex(8)
    email_sent = await send_login_code(email, verification_code)

    if not email_sent:
        raise HTTPException(
            status_code=500,
            detail="Failed to send login code email",
        )

    verification_code_hash = sha256(verification_code.encode()).digest().hex()
    await vk.set(
        f"auth:login_code:{verification_code_hash}",
        json.dumps(
            {
                "code": verification_code_hash,
                "email": email,
                "user_id": str(db_user.id),
            }
        ),
        ex=LOGIN_CODE_LIFETIME,
    )
    return {"status": "ok"}


@auth.post("/login-with-code")
async def login_with_code(
    request: Request,
    response: Response,
    code: str,
    db: AsyncSession = Depends(get_db_session),
):
    vk: valkey.Valkey = request.app.state.valkey

    is_host_ratelimited = await ratelimit(
        f"auth:login_code:ratelimit:{request.client.host}", LIMIT, WINDOW, vk
    )

    if is_host_ratelimited:
        raise HTTPException(
            status_code=429,
            detail="Too many requests",
        )

    login_code_hash = sha256(code.encode()).digest().hex()
    login_request_raw = await vk.get(f"auth:login_code:{login_code_hash}")

    if not login_request_raw:
        raise HTTPException(status_code=401, detail="Invalid code")

    login_request = json.loads(login_request_raw)

    db_user = await get_user_by_id(int(login_request["user_id"]), db)
    if not db_user:
        raise HTTPException(status_code=500, detail="Internal server error")

    is_email_ratelimited = await ratelimit(
        f"auth:login_code:ratelimit:{login_request['email']}", LIMIT, WINDOW, vk
    )

    if is_email_ratelimited:
        raise HTTPException(
            status_code=429,
            detail="Too many requests",
        )

    await vk.delete(f"auth:login_code:{login_code_hash}")

    session = await create_session(db_user, db)

    set_session_cookie(response, session.id)

    return {"status": "ok", "user_id": str(db_user.id)}
