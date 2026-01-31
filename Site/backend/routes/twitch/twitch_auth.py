from .router import twitch

import secrets
from datetime import timedelta

import valkey.asyncio as valkey
from fastapi import Request, HTTPException


BOT_SECRET_TTL = timedelta(minutes=5)


@twitch.get("/bot/secret")
async def twitch_auth_bot_secret(request: Request):
    vk: valkey.Valkey = request.app.state.valkey
    secret = secrets.token_urlsafe(32)
    await vk.set(
        f"twitch:bot:auth:secret:{secret}", "1", ex=BOT_SECRET_TTL.total_seconds()
    )
    return {"secret": secret}


@twitch.get("/bot/{secret}")
async def twitch_auth_bot(request: Request, secret: str):
    vk: valkey.Valkey = request.app.state.valkey
    if not await vk.get(f"twitch:bot:auth:secret:{secret}"):
        raise HTTPException(status_code=403, detail="Invalid secret")

    await vk.delete(f"twitch:bot:auth:secret:{secret}")
    return ""


@twitch.get("/user")
async def twitch_auth_user():
    return ""
