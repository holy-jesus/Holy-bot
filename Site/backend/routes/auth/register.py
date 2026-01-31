from .router import auth

import secrets
from typing import Annotated
from hashlib import sha256

from fastapi import Request, Response, Depends, Cookie, Header, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession

from Site.backend.services.auth.csrf import check_csrf_token
from Site.backend.services.auth.session import (
    create_temp_session,
    get_temp_session,
    create_session,
)
from Site.backend.services.auth.user import (
    email_already_exists,
    username_already_exists,
)
from Site.backend.services.auth.cookie import (
    set_session_cookie,
    set_temp_session_cookie,
)
from Site.backend.services.email import send_verification_code
from Site.backend.deps import get_db_session
from Site.backend.models import UserCreate
from holybot_shared.db_models import User


@auth.post("/register", status_code=202)
async def register_user(
    request: Request,
    response: Response,
    user: UserCreate,
    x_csrf_token: Annotated[str, Header(alias="X-CSRF-Token")],
    db: AsyncSession = Depends(get_db_session),
):
    csrf_cookie = request.cookies.get("csrf")
    if not csrf_cookie or csrf_cookie != x_csrf_token:
        raise HTTPException(status_code=403, detail="CSRF token mismatch")

    if not await check_csrf_token(x_csrf_token, request.app.state.valkey):
        raise HTTPException(status_code=403, detail="CSRF token is invalid")

    async with db.begin():
        if await email_already_exists(user.email, db):
            raise HTTPException(status_code=409, detail="Email already registered")

        if await username_already_exists(user.username, db):
            raise HTTPException(status_code=409, detail="Username already registered")

        verification_code = secrets.token_hex(8)

        email_sent = await send_verification_code(user.email, verification_code)
        if not email_sent:
            raise HTTPException(
                status_code=500,
                detail="Failed to send verification email",
            )

        temp_session = await create_temp_session(
            verification_code=verification_code,
            user=user,
            db=db,
        )

    set_temp_session_cookie(response, temp_session.id)

    response.delete_cookie("csrf")

    return {"status": "verification_required"}


@auth.post("/confirm-email")
async def confirm_email(
    request: Request,
    response: Response,
    code: Annotated[str, Body(embed=True)],
    temp_token: Annotated[str, Cookie(alias="temp_session")],
    db: AsyncSession = Depends(get_db_session),
):
    async with db.begin():
        temp_session = await get_temp_session(temp_token, db)
        if not temp_session:
            raise HTTPException(
                status_code=400, detail="Invalid or expired temp session"
            )

        input_hash = sha256(code.encode()).digest().hex()

        if not secrets.compare_digest(input_hash, temp_session.verification_code_hash):
            raise HTTPException(status_code=400, detail="Invalid verification code")

        if await email_already_exists(temp_session.email, db):
            raise HTTPException(status_code=409, detail="Email already registered")

        new_user = User(
            email=temp_session.email,
            username=temp_session.username,
            password_hash=temp_session.password_hash,
        )
        db.add(new_user)
        await db.flush()

        session = await create_session(new_user, db)

        await db.delete(temp_session)

    set_session_cookie(response, session.id)

    response.delete_cookie("temp_session")

    return {"status": "ok", "user_id": str(new_user.id)}
