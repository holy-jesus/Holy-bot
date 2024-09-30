import hmac
import time
from datetime import timedelta
import hashlib

import dateutil.parser
from fastapi import APIRouter, Request, Response, BackgroundTasks
import orjson

from utils import client, db, logger, SECRET


eventsub = APIRouter()


async def channel_update(event: dict):
    user = await db.users.find_one({"_id": event["event"]["broadcaster_user_id"]})
    if user["category"] != event["event"]["category_name"] and user["is_live"]:
        if user["category"] not in user["played_time"]:
            user["played_time"][user["category"]] = time.time() - user["game_time"] 
        else:
            user["played_time"][user["category"]] += time.time() - user["game_time"] 
        user["game_time"] = time.time()
    user["title"] = event["event"]["title"]
    user["category"] = event["event"]["category_name"]
    await db.users.update_one({"_id": user["_id"]}, {"$set": user})


async def stream_online(event: dict):
    user = await db.users.find_one({"_id": event["event"]["broadcaster_user_id"]})
    await client.send_event("recognizer", "online", {"login": user["login"]})
    started_at = time.time()
    await db.users.update_one({"_id": user["_id"]}, {"$set": {"is_live": True, "played_time": {}, "start_time": started_at, "game_time": started_at}})


async def stream_offline(event: dict):
    user = await db.users.find_one({"_id": event["event"]["broadcaster_user_id"]})
    await db.users.update_one({"_id": user["_id"]}, {"$set": {"is_live": False, "played_time": {}, "start_time": None, "game_time": None}})


async def user_update(event: dict):
    # Если чел меняет ник
    print(event)


async def user_authorization_revoke(event: dict):
    # Надо отключать пользователя
    print(event)


events = {
    "channel.update": channel_update,
    "stream.online": stream_online,
    "stream.offline": stream_offline,
    "user.update": user_update,
    "user.authorization.revoke": user_authorization_revoke,
}


def verify_hmac(request: Request, body: bytes) -> bool:
    twitch_hmac = request.headers.get("Twitch-Eventsub-Message-Signature", "").replace(
        "sha256=", ""
    )
    my_hmac = hmac.digest(
        SECRET.encode(),
        request.headers.get("Twitch-Eventsub-Message-Id", "").encode()
        + request.headers.get("Twitch-Eventsub-Message-Timestamp", "").encode()
        + body,
        hashlib.sha256,
    ).hex()
    return hmac.compare_digest(twitch_hmac, my_hmac)


def verify_time(request: Request) -> bool:
    twitch_time = dateutil.parser.isoparse(
        request.headers.get(
            "Twitch-Eventsub-Message-Timestamp", "2000-01-01T00:00:00+00:00"
        )
    ).timestamp()
    my_time = time.time()
    return my_time - twitch_time < 600


@eventsub.post("/eventsub")
async def event(request: Request, response: Response, background_tasks: BackgroundTasks):
    response.status_code = 204
    body = await request.body()
    try:
        event = orjson.loads(body)
    except orjson.JSONDecodeError:
        response.status_code = 400
        response.init_headers(response.headers)
        return response
    logger.debug(f"Новый ивент от твича, данные: {event}")
    message_type = request.headers.get("Twitch-Eventsub-Message-Type", "")
    type = event["subscription"]["type"]
    wrong_request = (
        (not verify_hmac(request, body))
        + (not verify_time(request))
        + (type not in events)
        + (
            message_type
            not in ("notification", "webhook_callback_verification", "revocation")
        )
    )
    if wrong_request != 0:
        response.status_code = 403
    elif message_type == "notification":
        background_tasks.add_task(events[type], event)
    elif message_type == "webhook_callback_verification":
        challenge = event["challenge"]
        response.status_code = 200
        response.media_type = "text/plain"
        response.body = response.render(challenge)
    elif message_type == "revocation":
        await client.send_event(
            "twitchapi", "error", {"name": "Subscription revocated", "text": str(event)}
        )
    response.init_headers(response.headers)
    return response
