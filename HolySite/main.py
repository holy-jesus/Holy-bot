import asyncio
from string import ascii_letters, digits
from random import choice
from os import getenv
import socket

import aiohttp
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

try:
    from routes import routes
    from utils import client, SCOPES, logged_in, templates, db, SECRET
except ImportError:
    from .routes import routes
    from .utils import client, SCOPES, logged_in, templates, db, SECRET

DEBUG = getenv("DEBUG") or False
DOMAIN = getenv('domain')

async def lifespan(_):
    client.loop = asyncio.get_event_loop()
    await client.connect()
    users = await db.users.find({"bot_enabled": True}).to_list(None)
    subscriptions = await client.send_event(
        "twitchapi", "get_eventsub_subscriptions", {}, True
    )
    types = [
        "channel.update",
        "stream.online",
        "stream.offline",
        # "user.update",
        # "user.authorization.revoke",
    ]
    status = {user["_id"]: types.copy() for user in users}
    for sub in subscriptions:
        user_id = (
            sub["condition"]["broadcaster_user_id"]
            if "broadcaster_user_id" in sub["condition"]
            else sub["condition"]["user_id"]
        )
        if "enabled" == sub["status"] and user_id in status:
            status[user_id].remove(sub["type"])
        if user_id not in status:
            await client.send_event(
                "twitchapi",
                "delete_eventsub_subscription",
                {"subscription_id": sub["id"]},
            )
    for user_id, subscriptions in status.items():
        for type in subscriptions:
            await client.send_event(
                "twitchapi",
                "create_eventsub_subscription",
                {
                    "user_id": user_id,
                    "subscription_type": type,
                    "callback": f"https://{DOMAIN}/eventsub",
                    "secret": SECRET,
                },
            )
    for user in users:
        stream_info = await client.send_event(
            "twitchapi",
            "get_user_information",
            {"user_id": user["_id"], "access_token": None},
            True,
        )
        await db.users.update_one({"_id": user["_id"]}, {"$set": stream_info})
    yield
    db.client.close()
    if client.connected.is_set():
        client.writer.close()
        await client.writer.wait_closed()


app = FastAPI(
    title="holy_bot",
    redoc_url=None,
    docs_url=None,
    debug=DEBUG,
    lifespan=lifespan,
)


@app.exception_handler(404)
async def notfound(request: Request, exc):
    return RedirectResponse("/")


@app.exception_handler(500)
async def internalservererror(request: Request, exc):
    return templates.TemplateResponse("500.html", {"request": request}, status_code=500)


app.mount("/static", StaticFiles(directory="./static"), name="static")
for route in routes:
    app.include_router(route)


@app.get("/")
@logged_in(False, True)
async def index(request: Request, response: Response, user=None):
    state = None
    if not user:
        state = "".join(choice(ascii_letters + digits) for _ in range(32))
        response.set_cookie("state", state)
    response = templates.TemplateResponse(
        "index_temp.html",
        {"request": request, "user": user, "state": state, "scope": SCOPES},
        headers=response.headers,
    )
    return response
