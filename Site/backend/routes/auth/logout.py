from .router import auth

from typing import Annotated

from fastapi import Cookie, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete

from holybot_shared.db import Session
from Site.backend.deps import get_db_session


@auth.post("/logout")
async def logout(
    response: Response,
    session_id: Annotated[str | None, Cookie(alias="session")] = None,
    db: AsyncSession = Depends(get_db_session),
):
    if session_id:
        await db.execute(delete(Session).where(Session.id == session_id))
        await db.commit()
    
    response.delete_cookie("session")
    return {"status": "ok"}
