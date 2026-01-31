import os
import secrets
from hashlib import sha256
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, exists, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from holybot_shared.db_models import User, Session, TempSession
from Site.backend.models import UserCreate
from Site.backend.services.auth.password import hash_password

SESSION_TTL = timedelta(days=int(os.getenv("SESSION_TTL_DAYS", "7")))
SESSION_REFRESH = timedelta(days=int(os.getenv("SESSION_REFRESH_DAYS", "5")))


async def create_session(user: User, db: AsyncSession) -> Session:
    new_session_token = secrets.token_urlsafe(32)
    while await db.scalar(select(exists().where(Session.id == new_session_token))):
        new_session_token = secrets.token_urlsafe(32)

    session = Session(
        id=new_session_token,
        user=user,
    )

    db.add(session)
    await db.flush()

    return session


async def get_session(
    session_token: str, db: AsyncSession
) -> tuple[bool, Session | None]:
    """
    Находит сессию, обновляет или удаляет, если сессия устарела.

    :param session_token: Сессия полученая от пользователя
    :param db: AsyncSession
    :return:
    """
    session: Session | None = (
        await db.execute(
            select(Session)
            .where(Session.id == session_token)
            .options(selectinload(Session.user))
        )
    ).scalar_one_or_none()
    if session is None:
        return True, None
    elif datetime.now(timezone.utc) >= (
        session.created_at + SESSION_LIFETIME
    ).astimezone(timezone.utc):
        await db.delete(session)
        return True, None
    elif datetime.now(timezone.utc) >= (
        session.created_at + SESSION_REFRESH
    ).astimezone(timezone.utc):
        await db.delete(session)
        return True, await create_session(session.user, db)
    return False, session


async def get_user_by_session(session_obj: Session, db: AsyncSession) -> User | None:
    return (
        await db.execute(
            select(User).where(User.sessions.any(Session.id == session_obj.id))
        )
    ).scalar_one_or_none()


async def create_temp_session(
    verification_code: str, user: UserCreate, db: AsyncSession
) -> TempSession:
    temp_session = TempSession(
        id=secrets.token_urlsafe(32),
        username=user.username,
        email=user.email,
        password_hash=hash_password(user.password),
        verification_code_hash=sha256(verification_code.encode()).digest().hex(),
    )

    db.add(temp_session)
    await db.flush()
    return temp_session


async def get_temp_session(temp_token: str, db: AsyncSession) -> TempSession | None:
    return (
        await db.execute(select(TempSession).where(TempSession.id == temp_token))
    ).scalar_one_or_none()
