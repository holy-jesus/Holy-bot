import asyncio
import os
import sys
from time import time
from datetime import datetime

import aiohttp
import orjson
from motor.motor_asyncio import AsyncIOMotorClient
from aiocache import Cache, cached
from dotenv import load_dotenv
from loguru import logger

from kafkaclient import Client

logger.remove()
logger.add(sys.stdout, level="TRACE", enqueue=True)

load_dotenv(".env")

TOKEN = os.getenv("twitch_token")
CLIENT_ID = os.getenv("app_id")
SECRET = os.getenv("app_secret")
LOOP = asyncio.new_event_loop()
asyncio.set_event_loop(LOOP)

client = Client("twitchapi", LOOP)

class TwitchApi:
    def __init__(self):
        self.bot_token = TOKEN
        self.client_id = CLIENT_ID
        self.secret = SECRET
        self.loop = LOOP
        self.token = None
        self.session = None
        self.expiration_time = time()
        self.headers = {"Client-Id": self.client_id}
        self.db = AsyncIOMotorClient(
            os.getenv("mongodb_link")
        )["holy_bot"]

    async def make_request(
        self, method, url, headers=None, params=None, data=None, json=None
    ):
        if self.session is None:
            self.session = aiohttp.ClientSession()
        response = await self.session.request(
            method, url, headers=headers, params=params, data=data, json=json
        )
        if response.status < 300:
            logger.debug(f"{method} {url} {response.status}")
        else:
            logger.error(f"{method} {url} {response.status}\n{await response.text()}")
            self.loop.create_task(
                self.error(
                    "TwitchAPI request",
                    f"{method} {url} {response.status}\n{await response.text()}",
                )
            )
        return response

    async def create_app_token(self):
        app_access_token = await self.db.config.find_one({"_id": "app_access_token"})
        if app_access_token and app_access_token["expiration_time"] > time():
            self.token = app_access_token["token"]
            self.expiration_time = app_access_token["expiration_time"]
            self.headers["Authorization"] = f"Bearer {self.token}"
            return
        resp = await self.make_request(
            "POST",
            f"https://id.twitch.tv/oauth2/token?client_id={self.client_id}&"
            f"client_secret={self.secret}&grant_type=client_credentials",
        )
        json = await resp.json(loads=orjson.loads)
        self.token = json["access_token"]
        self.expiration_time = json["expires_in"] + time() - 30
        self.headers["Authorization"] = f"Bearer {self.token}"
        await self.db.config.update_one(
            {"_id": "app_access_token"},
            {"$set": {"token": self.token, "expiration_time": self.expiration_time}},
            True,
        )

    async def refresh_user_token(self, user):
        response = await self.make_request(
            "POST",
            f"https://id.twitch.tv/oauth2/token?grant_type=refresh_token"
            f"&refresh_token={user['refresh_token']}&client_id={self.client_id}&client_secret={self.secret}",
        )
        if response.status == 401:
            access_token = None
            refresh_token = None
            expires = None
        else:
            js = await response.json(loads=orjson.loads)
            access_token = js["access_token"]
            refresh_token = js["refresh_token"]
            expires = js["expires_in"] + time()
        await self.db["users"].update_one(
            {"_id": user["_id"]},
            {
                "token": access_token,
                "refresh_token": refresh_token,
                "expires": expires,
            },
        )

    @client.event()
    async def user_logged_in(self, code: str):
        user = {}
        response = await self.make_request(
            "POST",
            "https://id.twitch.tv/oauth2/token"
            f"?client_id={self.client_id}&client_secret={self.secret}&code={code}&"
            "grant_type=authorization_code&redirect_uri=http://localhost:8000/login",
        )
        data = await response.json(loads=orjson.loads)
        user["access_token"] = data["access_token"]
        user["expires"] = data["expires_in"] + time()
        user["refresh_token"] = data["refresh_token"]
        data = await self.get_users(token=user["access_token"])
        user["id"] = data[0]["id"]
        user["login"] = data[0]["login"]
        return user

    @client.event()
    async def get_user_information(self, user_id: str, access_token: str):
        db_info = (await self.db.users.find_one({"id": user_id})) or {}
        stream_info = {
            "is_live": False,
            "stream_id": None,
            "game_time": None,
            "played_time": {},
            "start_time": None,
        }
        data = await self.get_channel_information([user_id], access_token)
        stream_info["title"] = data[0]["title"]
        stream_info["category"] = data[0]["game_name"]
        data = await self.get_streams([user_id], first=1, token=access_token)
        if data:
            stream_info["is_live"] = True
            stream_info["start_time"] = datetime.fromisoformat(
                data[0]["started_at"]
            ).timestamp()
            stream_id, vod_id = await self.get_current_stream(user_id)
            if vod_id:
                played_time, game_time = await self.get_played_time_from_stream(vod_id)
                if not game_time:
                    game_time = datetime.fromisoformat(
                        data[0]["started_at"]
                    ).timestamp()
                stream_info["game_time"] = game_time
                stream_info["played_time"] = played_time
            elif stream_id != db_info.get("stream_id", None):
                stream_info["game_time"] = datetime.fromisoformat(
                    data[0]["started_at"]
                ).timestamp()
            stream_info["stream_id"] = stream_id
        return stream_info

    async def get_current_stream(self, channel_id: str):
        request = await self.make_request(
            "POST",
            "https://gql.twitch.tv/gql",
            headers={"Client-Id": "kimne78kx3ncx6brgo4mv6wki5h1ko"},
            json=[
                {
                    "operationName": "FFZ_BroadcastID",
                    "variables": {"id": channel_id},
                    "extensions": {
                        "persistedQuery": {
                            "version": 1,
                            "sha256Hash": "cc89dfe8fcfe71235313b05b34799eaa519d162ebf85faf0c51d17c274614f0f",
                        }
                    },
                }
            ],
        )
        data = await request.json()
        stream_id = data[0]["data"]["user"]["stream"]["id"]
        vod_id = (
            data[0]["data"]["user"]["stream"]["archiveVideo"]["id"]
            if data[0]["data"]["user"]["stream"]["archiveVideo"]
            else None
        )
        return stream_id, vod_id

    async def get_played_time_from_stream(self, video_id: str):
        request = await self.make_request(
            "POST",
            "https://gql.twitch.tv/gql",
            headers={"Client-Id": "kimne78kx3ncx6brgo4mv6wki5h1ko"},
            json=[
                {
                    "operationName": "VideoPreviewCard__VideoMoments",
                    "variables": {"videoId": video_id},
                    "extensions": {
                        "persistedQuery": {
                            "version": 1,
                            "sha256Hash": "0094e99aab3438c7a220c0b1897d144be01954f8b4765b884d330d0c0893dbde",
                        }
                    },
                },
            ],
        )
        video_moments = await request.json()
        categories = {}
        game_time = None
        for edge in video_moments[0]["data"]["video"]["moments"]["edges"]:
            category = edge["node"]["details"]["game"]["displayName"]
            duration = edge["node"]["durationMilliseconds"] / 1000
            if duration == 0:
                position = edge["node"]["positionMilliseconds"] / 1000
                stream_duration = edge["node"]["video"]["lengthSeconds"]
                game_time = time() - (stream_duration - position)
            else:
                if category not in categories:
                    categories[category] = 0
                categories[category] += duration
        return categories, game_time

    @client.event()
    async def modify_channel_information(
        self, channel_id: str, game_name: str = None, title: str = None
    ):
        if self.token is None or self.expiration_time < time():
            await self.create_app_token()
        if game_name is None and title is None:
            return None
        headers = self.headers.copy()
        user = self.db["users"].find_one({"id": channel_id})
        if time() > user["expires"]:
            await self.refresh_user_token(user)
        headers["Authorization"] = f"Bearer {user['access_token']}"
        if game_name is not None:
            db_game = await self.db["games"].find_one({"names": game_name})
            if db_game is None:
                response = await self.make_request(
                    "GET",
                    f"https://api.twitch.tv/helix/games?name={game_name}",
                    headers=headers,
                )
                js = await response.json(loads=orjson.loads)
                if js["data"]:
                    game_dict = js["data"][0]
                    if db_game:
                        await self.db["games"].update_one(
                            db_game, {"$push": {"names": game_name}}
                        )
                    else:
                        db_game = {"id": game_dict["id"], "names": [game_dict["name"]]}
                        await self.db["games"].insert_one(db_game)
                else:
                    pass
                    # games = []
                    # async for db_game in self.db["games"].find():
                    #     games += db_game["names"]
                    # closest = difflib.get_close_matches(
                    #     game_name, [_game.name for _game in Game.select()], n=1, cutoff=0.70
                    # )
                    # if not closest:
                    #     if not connection.is_closed():
                    #         connection.close()
                    #     return {"channel_id": user.id, "success": False, "game": ""}
                    # else:
                    #     game_obj = Game.get(name=closest[0])
            response = await self.make_request(
                "PATCH",
                f"https://api.twitch.tv/helix/channels?broadcaster_id={channel_id}",
                headers=headers,
                json={"game_id": db_game["id"]},
            )
            if response.status == 204:
                return {
                    "channel_id": user["id"],
                    "success": True,
                    "game": db_game["names"][0],
                }
            else:
                return {"channel_id": user["id"], "success": False}
        else:
            response = await self.make_request(
                "PATCH",
                f"https://api.twitch.tv/helix/channels?broadcaster_id={channel_id}",
                headers=headers,
                json={"title": title},
            )
            if response.status == 204:
                return {"channel_id": user["id"], "success": True, "title": title}
            else:
                return {"channel_id": user["id"], "success": False}

    @client.event()
    async def get_streams(
        self,
        user_id: list = None,
        user_login: list = None,
        first: int = None,
        token: str = None,
    ):
        if self.token is None or self.expiration_time < time():
            await self.create_app_token()
        if not user_id and not user_login:
            return None
        headers = self.headers.copy()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        params = {"first": first}
        if user_id:
            params["user_id"] = user_id
        if user_login:
            params["user_login"] = user_login
        response = await self.make_request(
            "GET",
            "https://api.twitch.tv/helix/streams",
            params=params,
            headers=self.headers,
        )
        return (await response.json(loads=orjson.loads))["data"]

    @client.event()
    async def get_users(
        self, user_id: list = None, user_login: list = None, token: str = None
    ):
        if self.token is None or self.expiration_time < time():
            await self.create_app_token()
        headers = self.headers.copy()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        params = {}
        if user_id:
            params["user_id"] = user_id
        if user_login:
            params["user_login"] = user_login
        response = await self.make_request(
            "GET",
            "https://api.twitch.tv/helix/users",
            params=params,
            headers=headers,
        )
        return (await response.json(loads=orjson.loads))["data"]

    @client.event()
    async def get_channel_information(self, broadcaster_id: list, token: str = None):
        if self.token is None or self.expiration_time < time():
            await self.create_app_token()
        headers = self.headers.copy()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        params = {"broadcaster_id": broadcaster_id}
        response = await self.make_request(
            "GET",
            "https://api.twitch.tv/helix/channels",
            params=params,
            headers=headers,
        )

        return (await response.json(loads=orjson.loads))["data"]

    @client.event()
    async def create_eventsub_subscription(
        self, user_id, subscription_type, callback, secret
    ):
        if self.token is None or self.expiration_time < time():
            await self.create_app_token()
        headers = self.headers.copy()
        headers["Content-Type"] = "application/json"
        data = {
            "type": subscription_type,
            "version": "1",
            "condition": {"broadcaster_user_id": user_id},
            "transport": {
                "method": "webhook",
                "callback": callback,
                "secret": secret,
            },
        }
        response = await self.make_request(
            "POST",
            "https://api.twitch.tv/helix/eventsub/subscriptions",
            headers=headers,
            json=data,
        )
        return None

    @client.event()
    async def delete_eventsub_subscription(self, subscription_id: str):
        if self.token is None or self.expiration_time < time():
            await self.create_app_token()
        response = await self.make_request(
            "DELETE",
            "https://api.twitch.tv/helix/eventsub/subscriptions",
            params={"id": subscription_id},
            headers=self.headers,
        )
        return None

    @client.event()
    async def get_eventsub_subscriptions(self):
        if self.token is None or self.expiration_time < time():
            await self.create_app_token()
        response = await self.make_request(
            "GET",
            "https://api.twitch.tv/helix/eventsub/subscriptions",
            headers=self.headers,
        )
        return (await response.json(loads=orjson.loads))["data"]

    @client.event()
    async def send_whisper(self, from_user_id, to_user_id, message):
        headers = self.headers.copy()
        headers["Authorization"] = f"Bearer {self.bot_token}"
        params = {"from_user_id": from_user_id, "to_user_id": to_user_id}
        response = await self.make_request(
            "POST",
            "https://api.twitch.tv/helix/whispers",
            headers=headers,
            params=params,
            json={"message": message},
        )
        return response.status

    @client.event()
    async def delete_chat_messages(self, broadcaster_id, moderator_id, message_id=None):
        headers = self.headers.copy()
        headers["Authorization"] = f"Bearer {self.bot_token}"
        response = await self.make_request(
            "DELETE",
            f"https://api.twitch.tv/helix/moderation/chat?broadcaster_id={broadcaster_id}&moderator_id={moderator_id}{('&message_id=' + message_id) if message_id else ''}",
            headers=headers,
        )
        return response.status

    @client.event()
    async def send_chat_announcement(
        self, broadcaster_id, moderator_id, message, color=None
    ):
        headers = self.headers.copy()
        headers["Authorization"] = f"Bearer {self.bot_token}"
        js = {"message": message, "color": color or "primary"}
        response = await self.make_request(
            "POST",
            f"https://api.twitch.tv/helix/chat/announcements?broadcaster_id={broadcaster_id}&moderator_id={moderator_id}",
            headers=headers,
            json=js,
        )
        return response.status

    @client.event()
    async def ban_user(
        self,
        broadcaster_id: str,
        moderator_id: str,
        user_id: str,
        duration: int = None,
        reason: str = None,
    ):
        if self.token is None or self.expiration_time < time():
            await self.create_app_token()
        params = {"broadcaster_id": broadcaster_id, "moderator_id": moderator_id}
        data = {"data": {"user_id": user_id}}
        if duration:
            data["duration"] = duration
        if reason:
            data["reason"] = reason
        await self.make_request(
            "POST",
            "https://api.twitch.tv/helix/moderation/bans",
            headers=self.headers,
            params=params,
            json=data,
        )

    @client.event()
    @cached(cache=Cache.REDIS, ttl=3600, noself=True)
    async def get_emotes(self, channels_ids):
        if self.token is None or self.expiration_time < int(time()):
            await self.create_app_token()
        channels = {}
        response = await self.session.get("https://api.7tv.app/v2/emotes/global")
        global_7tv = [emote["name"] for emote in await response.json()]
        response = await self.session.get(
            "https://api.betterttv.net/3/cached/emotes/global"
        )
        global_bttv = [emote["code"] for emote in await response.json()]
        response = await self.session.get("https://api.frankerfacez.com/v1/set/global")
        global_ffz = []
        for set in (await response.json())["sets"].values():
            for emote in set["emoticons"]:
                global_ffz.append(emote["name"])
        for channel_id in channels_ids:
            response = await self.session.get(
                f"https://api.7tv.app/v2/users/{channel_id}/emotes"
            )
            channel_7tv_js = await response.json()
            if "status_code" not in channel_7tv_js:
                channel_7tv = [emote["name"] for emote in channel_7tv_js]
            else:
                channel_7tv = []
            response = await self.session.get(
                f"https://api.frankerfacez.com/v1/room/id/{channel_id}"
            )
            channel_ffz = []
            channel_ffz_js = await response.json()
            if "sets" in channel_ffz_js:
                for set in (await response.json())["sets"].values():
                    for emote in set["emoticons"]:
                        channel_ffz.append(emote["name"])
            response = await self.session.get(
                f"https://api.betterttv.net/3/cached/users/twitch/{channel_id}"
            )
            channel_bttv = []
            js = await response.json()
            if "channelEmotes" in js:
                for emote in js["channelEmotes"]:
                    channel_bttv.append(emote["code"])
            if "sharedEmotes" in js:
                for emote in js["sharedEmotes"]:
                    channel_bttv.append(emote["code"])
            channels[channel_id] = (
                global_7tv
                + global_bttv
                + global_ffz
                + channel_7tv
                + channel_bttv
                + channel_ffz
            )
        return channels

    @client.event()
    @cached(cache=Cache.REDIS, ttl=3600, noself=True)
    async def get_rules(self, channels_names):
        if self.token is None or self.expiration_time < int(time()):
            await self.create_app_token()
        channels_rules = {}
        operations = [
            {
                "operationName": "Chat_ChannelData",
                "variables": {"channelLogin": channel_name},
                "extensions": {
                    "persistedQuery": {
                        "version": 1,
                        "sha256Hash": "3c445f9a8315fa164f2d3fb12c2f932754c2f2c129f952605b9ec6cf026dd362",
                    }
                },
            }
            for channel_name in channels_names
        ]
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Client-Id": "kimne78kx3ncx6brgo4mv6wki5h1ko",
        }
        response = await self.session.post(
            "https://gql.twitch.tv/gql", headers=headers, json=operations
        )
        js = await response.json()
        for channel_rule in js:
            if channel_rule["data"]["channel"] is None:
                continue
            channel_id = int(channel_rule["data"]["channel"]["id"])
            rules = channel_rule["data"]["channel"]["chatSettings"]["rules"]
            while "" in rules:
                rules.remove("")
            text = ""
            for num, rule in enumerate(rules):
                if rule == "":
                    continue
                for punc in ["-", ".", ",", " "] * 2:
                    rule = rule.strip(punc)
                try:
                    if ":" in rule:
                        punc = ""
                    elif ":" in rules[num + 1]:
                        punc = ";"
                    else:
                        punc = ","
                except IndexError:
                    punc = "."
                text += f"{rule}{punc} "
            channels_rules[channel_id] = text.strip()
        return channels_rules

    def exception_handler(self, _, exc): ...

    def start(self):
        try:
            self.loop.set_exception_handler(self.exception_handler)
            self.loop.create_task(client.start())
            self.loop.run_forever()
        except Exception:
            self.loop.run_until_complete(client.stop())
            self.loop.stop()
