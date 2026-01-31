from .router import auth

from fastapi import Depends, HTTPException, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from Site.backend.deps import get_db_session
from Site.backend.services.auth.session import get_session
from Site.backend.services.auth.cookie import set_session_cookie


@auth.get("/me")
async def get_me(
    request: Request, response: Response, db: AsyncSession = Depends(get_db_session)
):
    session_id = request.cookies.get("session")
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    is_updated, session = await get_session(session_id, db)
    if not session:
        response.delete_cookie("session")
        raise HTTPException(status_code=401, detail="Invalid session")

    if is_updated:
        set_session_cookie(response, session.id)

    return {
        "id": session.user_id,
        "username": session.user.username,
        "email": session.user.email,
    }
