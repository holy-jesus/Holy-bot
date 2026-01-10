from types import NoneType

from authentication.token import create_session, set_token_cookie
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from sessions import client

login = APIRouter()


@login.get("/login")
async def _login(
    request: Request,
    code: str | None = None,
    scope: str | None = None,
    state: str | None = None,
):
    if not all(
        (code, scope is not None, state, state == request.cookies.get("state", None))
    ):
        return RedirectResponse("/")
    token = await client.send_event(
        "twitchapi",
        "user_logged_in",
        wait_for_response=True,
        response_timeout=10,
        code=code,
    )
    if not token or "error" in token:
        return RedirectResponse("/")
    encoded_jwt = await create_session(token["id"])
    response = RedirectResponse("/profile")
    set_token_cookie(response, encoded_jwt)
    return response


@login.get("/logout")
async def logout():
    response = RedirectResponse("/")
    response.delete_cookie("token")
    return response


@login.get("/check_token")
async def check_token():
    pass
