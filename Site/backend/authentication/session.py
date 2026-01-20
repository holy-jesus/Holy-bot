import secrets
from time import time

from fastapi import Response
from sqlalchemy import select

from holybot_shared.models import User, Session

TOKEN_LIFETIME = 60 * 60 * 24 * 7


async def create_session(user: User) -> Session:
    pass


async def get_session(session: str) -> Session | None:
    session_obj = select(Session).where(Session.id == session)
