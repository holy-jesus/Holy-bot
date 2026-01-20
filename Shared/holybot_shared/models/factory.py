import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.engine.url import URL


url = URL.create(
    drivername="postgresql",
    username=os.getenv("POSTGRES_USER", "holybot"),
    password=os.getenv("POSTGRES_PASSWORD", "password"),
    host=os.getenv("POSTGRES_HOST", "localhost"),
    port=os.getenv("POSTGRES_PORT", 5432),
    database=os.getenv("POSTGRES_DB", "holybot"),
)

engine = create_async_engine(url, echo=True)

async_session_factory = async_sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession
)
