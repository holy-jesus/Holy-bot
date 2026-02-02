from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession

from holybot_shared.db import User


async def email_already_exists(email: str, db: AsyncSession) -> bool:
    result = await db.execute(select(exists().where(User.email == email)))
    return bool(result.scalar_one_or_none())


async def username_already_exists(username: str, db: AsyncSession) -> bool:
    result = await db.execute(select(exists().where(User.username == username)))
    return bool(result.scalar_one_or_none())


async def get_user_by_id(user_id: str, db: AsyncSession) -> User | None:
    return (
        await db.execute(select(User).where(User.id == user_id))
    ).scalar_one_or_none()


async def get_user_by_username(username: str, db: AsyncSession) -> User | None:
    return (
        await db.execute(select(User).where(User.username == username))
    ).scalar_one_or_none()


async def get_user_by_email(email: str, db: AsyncSession) -> User | None:
    return (
        await db.execute(select(User).where(User.email == email))
    ).scalar_one_or_none()
