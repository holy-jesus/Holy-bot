from collections.abc import AsyncGenerator
from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, Cookie, Response

from holybot_shared.db import User, factory
from Site.backend.services.auth.session import get_session
from Site.backend.services.auth.cookie import set_session_cookie


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with factory() as session:
        yield session


async def get_user(
    response: Response,
    session_id: Annotated[str, Cookie(alias="session")],
    db: AsyncSession = Depends(get_db_session),
) -> User:
    is_updated, session = await get_session(session_id, db)
    if not session:
        raise HTTPException(status_code=401, detail="Not authenticated")

    if is_updated:
        set_session_cookie(response, session.id)

    return session.user


async def admin_required(
    user: User = Depends(get_user),
) -> User:
    if not user.is_admin:
        raise HTTPException(403)
    return user
