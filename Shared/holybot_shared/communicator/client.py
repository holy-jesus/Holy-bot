import asyncio
import os
import inspect
from typing import Callable
from holybot_shared.SharedProto.google.protobuf import Any

import nats
import orjson
from loguru import logger
from nats.aio.client import Client as NATSClient
from nats.aio.msg import Msg
from nats.errors import TimeoutError as NatsTimeoutError
from betterproto2 import Message

from holybot_shared.communicator.stub import API
from holybot_shared.SharedProto.holybot.api import Event, SimpleResponse


class Client:
    def __init__(
        self,
        name: str,
    ) -> None:
        self.__name: str = name
        self.__nats_url: str = os.getenv("NATS_URL")
        self.__class_instance: object = None
        self._nc: NATSClient | None = None
        self.__events: dict[str, Callable] = {}
        self._wrapped_class_ref = None

        self.API = API(self)

    async def connect(self):
        self._nc = await nats.connect(self.__nats_url)

        await self._nc.subscribe(
            self.__name, cb=self.__nats_callback, queue=self.__name
        )
        logger.info(
            f"Client {self.__name} started and listening on subject '{self.__name}'"
        )

    async def close(self):
        if self._nc:
            await self._nc.drain()
            await self._nc.close()

    async def __nats_callback(self, msg: Msg):
        """Callback функция, вызываемая NATS при получении сообщения"""
        try:
            await self.__on_message(msg)
        except Exception as e:
            logger.exception(e)

    async def send_event(
        self,
        receiver: str,
        function_name: str,
        response_type: Message,
        wait_for_response: bool,
        timeout: float,
        payload: Message,
    ):

        payload_any = Any.pack(payload)

        event = Event(function_name=function_name, payload=payload_any)

        try:
            logger.info(f"wait_for_response: {wait_for_response}")
            if wait_for_response:
                response_msg: Msg = await self._nc.request(
                    receiver, bytes(event), timeout=timeout
                )

                response_data = response_msg.data

                logger.trace(f"Response from {receiver}: {response_data}")

                return response_type.parse(response_data)
            else:
                await self._nc.publish(receiver, bytes(event))
                return None
        except NatsTimeoutError:
            logger.error(
                f"Timeout waiting for response from {receiver} (event: {function_name})"
            )
            return None
        except Exception as e:
            logger.error(f"Error sending event: {e}")
            return None

    def event(self, name: str = None):
        def wrapper(func):
            nonlocal name
            if name is None:
                name = func.__name__
            self.__events[name] = func
            return func

        if inspect.isfunction(name):
            func = name
            name = func.__name__
            return wrapper(func)
        return wrapper

    def wrap_class(self, _class):
        self._wrapped_class_ref = _class

        def wrapper(*args, **kwargs):
            self.__class_instance = _class(*args, **kwargs)
            return self.__class_instance

        return wrapper

    def get_registered_events(self):
        return self.__events

    async def __on_message(self, msg: Msg):
        event = Event.parse(msg.data)
        func = self.__events.get(event.function_name, None)
        if func is None:
            logger.error(f"Unknown function: {event.function_name}.")
            return

        payload = event.payload
        if payload is None:
            payload = {}
        else:
            payload = payload.unpack()

        try:
            if inspect.iscoroutinefunction(func):
                result: Message = await func(self.__class_instance, payload)
            else:
                result: Message = func(self.__class_instance, payload)
        except Exception as e:
            logger.exception(f"Error executing event {event.function_name}")
            result = SimpleResponse(success=False, message=str(e))

        if msg.reply:
            await self._nc.publish(msg.reply, bytes(result))
