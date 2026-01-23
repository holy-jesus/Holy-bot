from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession

from holybot_shared.models import User


async def email_already_exists(email: str, db: AsyncSession) -> bool:
    result = await db.execute(select(exists().where(User.email == email)))
    return bool(result.scalar_one_or_none())


async def username_already_exists(username: str, db: AsyncSession) -> bool:
    result = await db.execute(select(exists().where(User.username == username)))
    return bool(result.scalar_one_or_none())
