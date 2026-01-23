from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from holybot_shared.models.factory import async_session_factory


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session
