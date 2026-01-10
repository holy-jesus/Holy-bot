import asyncio
import os
import sys
import logging
from asyncio import CancelledError
from typing import Literal

from websockets.asyncio.client import connect, ClientConnection
from dotenv import load_dotenv
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient
from websockets.exceptions import (
    ConnectionClosed,
    WebSocketException,
)

from kafkaclient import Client
from .channels import Channels


load_dotenv(".env")


logger.remove()
logger.add(sys.stdout, level="TRACE", enqueue=True)

HOST = "wss://irc-ws.chat.twitch.tv:443"
KAPPA = "kappa"
LOOP = asyncio.new_event_loop()
TOKEN = os.getenv("twitch_token")
MONGODB_USERNAME = os.getenv("mongodb_username")
MONGODB_PASSWORD = os.getenv("mongodb_password")
asyncio.set_event_loop(LOOP)

client = Client("twitchbot", LOOP)


@client.wrap_class
class TwitchBot:
    def __init__(self) -> None:
        self.token = TOKEN
        self.loop = LOOP

        self.ws: ClientConnection = None
        self.bot: dict = {"display-name": "hoIy_bot", "login": "hoiy_bot"}

        self.db = AsyncIOMotorClient(
            username=MONGODB_USERNAME,
            password=MONGODB_PASSWORD,
            connect=False,
        )["holy_bot"]

        self.channels = Channels(self)
        # self.timer = Timer(self)

        self.connected: asyncio.Event = asyncio.Event()
        self.thread_task: asyncio.Task = None
        self._internal_events = {
            "PRIVMSG": self._privmsg,
            "PING": self._ping,
            "NOTICE": self._notice,
            "JOIN": self._join,
            "PART": self._part,
            "GLOBALUSERSTATE": self._globaluserstate,
        }

    # Start and connect

    def run(self) -> None:
        try:
            self.loop.create_task(client.start())
            self.loop.create_task(self._connect())
            self.loop.run_forever()
        finally:
            self.loop.run_until_complete(self.close())
            self.loop.stop()

    async def close(self):
        if self.thread_task:
            self.thread_task.cancel()
        if self.ws:
            await self.ws.close()
        await client.stop()
        self.db.client.close()

    async def _connect(self) -> None:
        while True:
            try:
                websocket_logger = logging.Logger("logger")
                formatter = logging.Formatter(
                    "%(asctime)s;%(levelname)s;%(message)s", "%Y-%m-%d %H:%M:%S"
                )
                sh = logging.StreamHandler()
                sh.setLevel(logging.INFO)
                sh.setFormatter(formatter)
                websocket_logger.addHandler(sh)
                if self.ws:
                    await self.ws.close()
                self.ws = await connect(
                    HOST,
                    logger=websocket_logger,
                )
                break
            except Exception:
                logger.warning(
                    "Не могу подключиться к Twitch, повторная попытка через 15 секунд..."
                )
                await asyncio.sleep(15)
        await self._send(
            "CAP REQ :twitch.tv/commands twitch.tv/membership twitch.tv/tags"
        )
        await self._send(f"PASS oauth:{self.token}")
        await self._send(f"NICK {KAPPA}")
        await self.channels.join_all_channels()
        self.thread_task = self.loop.create_task(self._thread())

    # Heart

    async def _thread(self) -> None:
        logger.debug("_thread был запущен")
        self.connected.set()
        try:
            while True:
                data = await self.ws.recv()
                if data:
                    for event in data.split("\r\n"):
                        if not event:
                            continue
                        logger.trace(f"< {event}")
                        self.loop.create_task(self._process_event(event))
                else:
                    logger.error("Соединение скорее всего закрыто.")
                    raise Exception("CONNECTION CLOSED")
        except CancelledError:
            return
        except Exception as e:
            logger.exception(e)
            self.connected.clear()
            await self._connect()

    async def _process_event(self, data: str) -> None:
        data = data.strip()
        parsed = self._parse_event(data)
        if not parsed:
            return
        command = parsed["command"]
        try:
            await self._internal_events[command](parsed)
        except Exception as e:
            logger.exception(e)

    # Sending messages

    async def send_chat_message_by_id(self, text: str, id: str = None):
        channel = self.channels.get(id)
        login = channel["login"]
        await self.send_chat_message(text, login)

    async def send_chat_message(self, text: str, login: str):
        await self._send_privmsg(text, login)

    async def _send(self, data: str) -> None:
        try:
            logger.trace(f"> {data}")
            await self.ws.send(data + "\r\n")
        except ConnectionClosed:
            pass

    async def _send_privmsg(self, text: str, login: str):
        privmsg = f"PRIVMSG #{login} :"
        text = text.strip()[:499]
        await self._send(privmsg + text)

    # Handling channels

    @client.event("channel_connected")
    async def join_channels(
        self, ids: list[str] = None, logins: list[str] = None, init: bool = False
    ):
        if not logins:
            logins = []
        if ids:
            for id in ids:
                login = (await self.channels.get_from_db(id=id))["login"]
                logins.append(login)
        if not init:
            self.channels.init_statuses(logins)
        join = ",".join(f"#{login}" for login in logins)
        if join:
            await self._send(f"JOIN {join}")
        if not init:
            statuses = await self.channels.get_statuses(logins)
            return statuses

    @client.event("channel_disconnected")
    async def leave_channels(self, ids: list[str] = None, logins: list[str] = None):
        if not logins:
            logins = []
        else:
            for login in logins:
                self.channels.pop(login=login)
        if ids:
            for id in ids:
                login = self.channels.pop(id=id)["login"]
                logins.append(login)
        part = ",".join(f"#{login}" for login in logins)
        if part:
            await self._send(f"PART {part}")

    # API

    async def delete_chat_messages(self, broadcaster_id, message_id=None):
        await self.make_api_request(
            "delete_chat_messages",
            broadcaster_id=broadcaster_id,
            moderator_id=self.bot["user-id"],
            message_id=message_id,
        )

    async def send_chat_announcement(
        self,
        text: str,
        broadcaster_id: str,
        color: Literal["blue", "green", "orange", "purple"] = None,
    ):
        await self.make_api_request(
            "send_chat_announcement",
            broadcaster_id=broadcaster_id,
            moderator_id=self.bot["user-id"],
            text=text,
            color=color,
        )

    async def ban_user(self, broadcaster_id, user_id, duration=None, reason=None):
        await self.make_api_request(
            "ban_user",
            broadcaster_id=broadcaster_id,
            moderator_id=self.bot["user-id"],
            user_id=user_id,
            duration=duration,
            reason=reason,
        )

    async def make_api_request(self, event: str, **kwargs):
        await client.send_event("twitchapi", event, **kwargs)

    # Parsing events

    def _parse_event(self, message: str) -> dict:
        idx = 0
        event = {"text": None, "command": None}
        # Tags
        if message[idx] == "@":
            end_idx = message.find(" ")
            self._parse_tags(message[1:end_idx], event)
            idx = end_idx + 1
        # Source
        if message[idx] == ":":
            idx += 1
            end_idx = message.find(" ", idx)
            source_parts = message[idx:end_idx].split("!")
            event["login"] = source_parts[0] if len(source_parts) == 2 else None
            idx = end_idx + 1
        end_idx = message.find(":", idx)
        if end_idx == -1:
            end_idx = len(message)
        command_parts = message[idx:end_idx].strip().split(" ")
        if command_parts[0] in self._internal_events:
            event["command"] = command_parts[0]
            if len(command_parts) == 2:
                event["channel"] = command_parts[1].replace("#", "")
        else:
            return None
        if end_idx != len(message):
            idx = end_idx + 1
            event["text"] = message[idx:]
        return event

    @staticmethod
    def _parse_tags(tags: str, event: dict) -> None:
        tags_to_ignore = ("client-nonce", "flags", "emote-sets")
        parsed_tags = tags.split(";")
        for tag in parsed_tags:
            parsed_tag = tag.split("=")
            if parsed_tag[1] in tags_to_ignore:
                continue
            elif not parsed_tag[1]:
                event[parsed_tag[0]] = None
            elif parsed_tag[0] in ("badges", "badge-info"):
                event[parsed_tag[0]] = tuple(
                    pair.split("/")[0] for pair in parsed_tag[1].split(",")
                )
            elif parsed_tag[0] == "emotes":
                event[parsed_tag[0]] = {}
                for emote in parsed_tag[1].split("/"):
                    emote_parts = emote.split(":")
                    event[parsed_tag[0]][emote_parts[0]] = []
                    positions = emote_parts[1].split(",")
                    for position in positions:
                        position_parts = position.split("-")
                        event[parsed_tag[0]][emote_parts[0]].append(
                            {
                                "start_position": position_parts[0],
                                "end_position": position_parts[1],
                            }
                        )
            elif parsed_tag[0] in (
                "first-msg",
                "mod",
                "subscriber",
                "turbo",
                "emote-only",
            ):
                event[parsed_tag[0]] = parsed_tag[1] == "1"
            elif parsed_tag[0] in ("tmi-sent-ts"):
                event[parsed_tag[0]] = int(parsed_tag[1]) / 1000
            else:
                event[parsed_tag[0]] = parsed_tag[1]

    # Events

    async def _privmsg(self, parsed: dict) -> None:
        if parsed["user-id"] == self.bot["user-id"]:
            return
        # await self.commands.execute_command(parsed)

    async def _ping(self, _) -> None:
        await self._send("PONG :tmi.twitch.tv")

    async def _join(self, parsed: dict) -> None:
        if parsed["login"] == self.bot["login"]:
            self.channels.set_status(
                parsed["channel"],
                {"success": True, "error": None, "status": "connected"},
            )

    async def _part(self, parsed: dict) -> None:
        if parsed["login"] == self.bot["login"]:
            channel = self.channels.get(login=parsed["channel"])
            if not channel:
                logger.info(f"Успешно вышел из {parsed['channel']} канала")
            else:
                logger.warning(f"Бот был забанен на {parsed['channel']} канале")
                await self.db.users.update_one(
                    {"login": parsed["channel"]}, {"$set": {"bot_enabled": False}}
                )
                self.channels.pop(login=parsed["channel"])

    async def _notice(self, parsed: dict) -> None:
        msg_id = parsed["msg-id"]
        if msg_id == "msg_banned":
            self.channels.set_status(
                parsed["channel"], {"success": False, "error": "banned"}
            )
            self.channels.pop(login=parsed["channel"])
            await self.db.users.update_one(
                {"login": parsed["channel"]}, {"$set": {"bot_enabled": False}}
            )
        elif msg_id == "msg_channel_suspended":
            self.channels.set_status(
                parsed["channel"], {"success": False, "error": "channel_suspended"}
            )
            self.channels.pop(login=parsed["channel"])
            await self.db.users.update_one(
                {"login": parsed["channel"]}, {"$set": {"bot_enabled": False}}
            )

    async def _globaluserstate(self, parsed: dict) -> None:
        self.bot.update(parsed)
        self.bot["login"] = self.bot["display-name"].lower()
        logger.info(f"Успешно залогинился как {self.bot['display-name']}")
