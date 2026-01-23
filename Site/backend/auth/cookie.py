from fastapi import Response

from holybot_shared.models import Session, TempSession


def set_session_cookie(response: Response, session: Session):
    response.set_cookie(
        key="session",
        value=session.id,
    )


def set_temp_session_cookie(response: Response, temp_session: TempSession):
    response.set_cookie(
        key="temp_session",
        value=temp_session.id,
        max_age=3600,
    )
