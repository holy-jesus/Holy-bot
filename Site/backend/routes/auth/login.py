from .auth import auth

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from Site.backend.deps import get_db_session
from Site.backend.models import (
    UserLoginWithEmail,
    UserLoginWithPassword,
)


@auth.post("/login")
async def login_user(
    user: UserLoginWithPassword, db: AsyncSession = Depends(get_db_session)
):
    pass


@auth.post("/login-with-email")
async def login_user_with_email(
    email: UserLoginWithEmail, db: AsyncSession = Depends(get_db_session)
):
    pass
