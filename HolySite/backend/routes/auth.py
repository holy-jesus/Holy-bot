import secrets

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, HTMLResponse

from sessions import db, client
from token_handler import create_session, verify_session, set_token_cookie, LIFETIME

auth = APIRouter()


@auth.get("/login")
async def login(
    request: Request,
    code: str = None,
    scope: str = None,
    state: str = None,
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
    print(token)
    if not token or "error" in token:
        return RedirectResponse("/")
    encoded_jwt = await create_session(token["id"])
    response = RedirectResponse("/profile")
    set_token_cookie(response, encoded_jwt)
    return response


@auth.get("/logout")
async def logout():
    pass
