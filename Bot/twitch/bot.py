import asyncio
import os
from enum import Enum
from typing import Annotated

from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError
import websockets.asyncio.client
from loguru import logger
import orjson
import uvloop

from models import Message, MessageType

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

WS_URL = (
    "wss://eventsub.wss.twitch.tv/ws"
    if os.getenv("APP_ENV") == "prod"
    else "ws://localhost:8080/ws"  # TODO
)

ERRORS = {
    4000: {
        "reason": "Internal server error",
        "note": "Indicates a problem with the server (similar to an HTTP 500 status code).",
    },
    4001: {
        "reason": "Client sent inbound traffic",
        "note": "Sending outgoing messages to the server is prohibited with the exception of pong messages.",
    },
    4002: {
        "reason": "Client failed ping-pong",
        "note": "You must respond to ping messages with a pong message.",
    },
    4003: {
        "reason": "Connection unused",
        "note": "When you connect to the server, you must create a subscription within 10 seconds or the connection is closed.",
    },
    4004: {
        "reason": "Reconnect grace time expired",
        "note": "When you receive a session_reconnect message, you have 30 seconds to reconnect to the server and close the old connection.",
    },
    4005: {"reason": "Network timeout", "note": "Transient network timeout."},
    4006: {"reason": "Network error", "note": "Transient network error."},
    4007: {"reason": "Invalid reconnect", "note": "The reconnect URL is invalid."},
}


class TwitchBot:
    def __init__(
        self,
        client_id: str,
    ) -> None:
        self._headers = {
            "Client-Id": client_id,
            "Content-Type": "application/json",
        }
        self._websockets: dict[str, websockets.ClientConnection] = {}
        self._functions = {}

    # Internal events

    def _welcome(self, ws: websockets.ClientConnection, message: Message) -> tuple[str, int]:
        session = message.payload
        self._websockets[session["id"]] = ws
        return session["id"], session["keepalive_timeout_seconds"] + 2

    async def _notification(self, session_id: str, message: Message):
        id = event["subscription"]["id"]
        if id in self._functions:
            await self._functions[id](event)

    async def _revocation(self, session_id: str, message: Message):
        pass

    async def _reconnect(self, session_id: str, message: Message):
        logger.info("reconnecting")
        await self._connect(event["session"]["reconnect_url"], session_id)

    async def _keepalive(self, message: Message):
        message.metadata

    # Connecting and health

    async def _connect(self, url: str = None, parent_id: str = None):
        if not url:
            url = WS_URL

        ws = await websockets.connect(
            url,
            # ping_interval=None,
            # ping_timeout=None,
        )
        self.loop.create_task(self._loop(ws, parent_id))

    async def _loop(
        self, ws: websockets.ClientConnection, parent_id: str = None
    ) -> None:
        event = orjson.loads(await ws.recv())
        session_id, timeout = self._welcome(ws, event)
        if parent_id:
            if not self._websockets[parent_id].closed:
                await self._websockets[parent_id].close()
            del self._websockets[parent_id]
        session_id = None
        timeout = 5.0
        try:
            while True:
                try:
                    event = orjson.loads(
                        await asyncio.wait_for(ws.recv(), timeout=timeout)
                    )
                except TimeoutError:
                    await self._connect(parent_id=session_id)
                    return
                logger.info(event)
                message = Message(*event)
                if message.metadata.message_type == MessageType.WELCOME:
                    session_id, timeout = self._welcome()
                elif message.metadata.message_type == MessageType.KEEPALIVE:
                    self._keepalive(message)
                elif message.metadata.message_type == MessageType.NOTIFICATION:
                    self._notification()
                elif message.metadata.message_type == MessageType.RECONNECT:
                    self._reconnect()
                elif message.metadata.message_type == MessageType.REVOKE:
                    self._revocation()
                else:
                    logger.error(
                        f"Unknown message_type: {message.metadata.message_type}"
                    )
        except ConnectionClosedOK:
            pass
        except ConnectionClosedError:
            logger.error(
                ERRORS.get(ws.close_code, f"Websocket closed with {ws.close_code} code")
            )
        except Exception as e:
            logger.error(e)

    # Starting and exiting

    def run(self):
        if self._subscriptions:
            self.loop.create_task(self._connect())
        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            self.loop.run_until_complete(self.exit())

    async def exit(self):
        for connection in self._websockets.values():
            await connection.close()

    def start(self):
        self.loop.create_task(self._connect())
