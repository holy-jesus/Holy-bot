from fastapi import Response

from Site.backend.services.auth.session import SESSION_TTL


def set_session_cookie(response: Response, value: str):
    response.set_cookie(
        key="session",
        value=value,
        max_age=int(SESSION_TTL.total_seconds()),
        secure=True,
        samesite="lax",
        httponly=True,
    )


def set_temp_session_cookie(response: Response, value: str):
    response.set_cookie(
        key="temp_session",
        value=value,
        max_age=3600,
        secure=True,
        samesite="lax",
    )
