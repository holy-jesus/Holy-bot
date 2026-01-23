from .auth import auth

from typing import Annotated

from fastapi import Request, Response, Header
from fastapi.responses import JSONResponse

from Site.backend.auth.csrf import create_csrf_token


@auth.get("/csrf")
async def issue_csrf(request: Request, response: JSONResponse):
    ip = request.client.host
    token = await create_csrf_token(ip, request.app.state.valkey)
    response = JSONResponse({"csrf": token})
    response.set_cookie(
        "csrf",
        token,
        samesite="lax",
        secure=True,
    )
    return response
