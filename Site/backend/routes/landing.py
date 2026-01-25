from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from Site.backend.deps import get_db_session
from holybot_shared.db_models import User

landing = APIRouter(prefix="/landing")


@landing.get("/channels")
async def get_channels(db: AsyncSession = Depends(get_db_session)):
    count = await db.scalar(select(func.count(User.id)))
    return {"channels": count or 0}
