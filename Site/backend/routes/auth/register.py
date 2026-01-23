from .auth import auth

import secrets
from typing import Annotated

from fastapi import Request, Response, Depends, Cookie, Header, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession

from Site.backend.auth.csrf import check_csrf_token
from Site.backend.auth.session import create_temp_session
from Site.backend.auth.cookie import set_temp_session_cookie
from Site.backend.auth.user import email_already_exists, username_already_exists
from Site.backend.auth.email import send_email
from Site.backend.deps import get_db_session
from Site.backend.models import UserCreate


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

    if await email_already_exists(user.email, db):
        raise HTTPException(status_code=409, detail="Email already registered")

    if await username_already_exists(user.username, db):
        raise HTTPException(status_code=409, detail="Username already registered")

    verification_code = secrets.token_hex(8)

    email_sent = await send_email(user.email, verification_code)
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

    set_temp_session_cookie(response, temp_session)
    response.delete_cookie("csrf")

    return {"status": "verification_required"}


@auth.post("/confirm-email")
async def confirm_email(
    code: Annotated[str, Body()],
    temp_token: Annotated[str, Cookie()],
    db: AsyncSession = Depends(get_db_session),
):
    temp_token
