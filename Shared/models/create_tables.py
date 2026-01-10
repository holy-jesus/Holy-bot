from sqlalchemy.schema import CreateTable

from .base import Base
from .factory import engine


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
