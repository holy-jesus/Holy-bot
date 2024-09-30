from time import time
from os import getenv

from fastapi import APIRouter, Request, Response
from fastapi.responses import RedirectResponse

from utils import logged_in, client, templates, db, SECRET

profile = APIRouter()


async def is_rate_limited(user_id: str):
    rate_limit = await db.ratelimit.find_one({"_id": user_id})
    if not rate_limit:
        rate_limit = {"_id": user_id, "value": []}
    for t in rate_limit["value"]:
        if (time() - t) > 300:
            rate_limit["value"].remove(t)
    if len(rate_limit["value"]) >= 5:
        return True
    rate_limit["value"].append(time())
    await db.ratelimit.update_one({"_id": user_id}, {"$set": rate_limit}, upsert=True)
    return False


@profile.get("/profile")
@logged_in
async def profile_get(request: Request, response: Response, user=None):
    if not user:
        return RedirectResponse("/")
    response = templates.TemplateResponse(
        "profile.html", {"request": request, "user": user}, headers=response.headers
    )
    return response


@profile.post("/profile")
@logged_in
async def profile_post(request: Request, response: Response, user=None):
    if not user:
        return RedirectResponse("/")
    if await is_rate_limited(user["_id"]):
        return Response(status_code=429)
    if user.get("connecting", False):
        return Response(status_code=400)
    await db.users.update_one({"_id": user["_id"]}, {"$set": {"connecting": True}})
    if not user["bot_enabled"]:
        user_information = await client.send_event(
            "twitchapi",
            "get_user_information",
            {"user_id": user["_id"], "access_token": None},
            True,
            5.0,
        )
        status = (
            await client.send_event(
                "twitchbot",
                "channel_connected",
                {"logins": [user["login"]]},
                wait_for_answer=True,
                timeout=5.0,
            )
        )[user["login"]]
        user_information["connecting"] = False
        if status["success"]:
            user_information["bot_enabled"] = True
        if not (await db.commands.find_one({"user_id": user["_id"]})):
            await db.commands.insert_many(
                [{
                    "user_id": user["_id"],
                    "aliases": ["title", "название"],
                    "response": "${ping}, ${title}",
                    "cooldown": {"global": 10, "user": 10},
                },
                {
                    "user_id": user["_id"],
                    "aliases": [
                        "music",
                        "song",
                        "musik",
                        "track",
                        "песня",
                        "музыка",
                        "трек",
                    ],
                    "response": "${ping}, ${song}",
                    "cooldown": {"global": 10, "user": 10},
                },
                {
                    "user_id": user["_id"],
                    "aliases": ["games", "играли", "игры"],
                    "response": "${ping}, ${games}",
                    "cooldown": {"global": 10, "user": 10},
                },
                {
                    "user_id": user["_id"],
                    "aliases": ["gametime", "игровремя", "game", "playtime", "игра"],
                    "response": "${ping}, ${gametime}",
                    "cooldown": {"global": 10, "user": 10},
                }]
            )
        types = [
            "channel.update",
            "stream.online",
            "stream.offline",
            # "user.update",
            # "user.authorization.revoke",
        ]
        for type in types:
            await client.send_event("twitchapi", 'create_eventsub_subscription', {"user_id": user["_id"], "subscription_type": type, "callback": f"https://{getenv('domain')}/eventsub", "secret": SECRET})
        await db.users.update_one({"_id": user["_id"]}, {"$set": user_information})
        return status
    else:
        await client.send_event(
            "twitchbot", "channel_disconnected", {"logins": [user["login"]]}
        )
        await db.users.update_one(
            {"_id": user["_id"]}, {"$set": {"bot_enabled": False, "connecting": False}}
        )
        return {"success": True, "status": "disconnected", "error": None}

