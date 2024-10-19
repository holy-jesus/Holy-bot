from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

auth = APIRouter()


@auth.get("/login")
async def login(
    request: Request,
    code: str = None,
    scope: str = None,
    state: str = None,
):
    if not all((code, scope, state, state == request.cookies.get("state", None))):
        return RedirectResponse("/")
    pass


@auth.get("/logout")
async def logout():
    pass
