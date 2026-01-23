from .auth import auth

from typing import Annotated

from fastapi import Request, Response, Header, HTTPException
from fastapi.responses import JSONResponse

from Site.backend.auth.csrf import create_csrf_token


@auth.get("/csrf")
async def issue_csrf(request: Request, response: JSONResponse):
    ip = request.client.host
    try:
        token = await create_csrf_token(ip, request.app.state.valkey)
    except RuntimeError:
        raise HTTPException(status_code=429, detail="Too many requests")
    response = JSONResponse({"csrf": token})
    response.set_cookie(
        "csrf",
        token,
        samesite="lax",
        secure=True,
    )
    # response.headers["X-RateLimit-Limit"] = "1"
    # response.headers["X-RateLimit-Remaining"] = "0"
    # response.headers["X-RateLimit-Reset"] = "60"
    return response
