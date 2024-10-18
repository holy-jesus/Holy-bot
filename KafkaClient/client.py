import uuid
import asyncio
from asyncio import BaseEventLoop, CancelledError, Future, Task
from inspect import iscoroutinefunction, isfunction

import orjson
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from loguru import logger


class Client:
    def __init__(self, name: str, loop: BaseEventLoop) -> None:
        self.__name: str = name
        self.__loop: BaseEventLoop = loop
        self.__poll_task: Task = None
        self.__class_instance: object = None
        self._consumer: AIOKafkaConsumer | None = None
        self._producer: AIOKafkaProducer | None = None
        self.__events: dict[str, callable] = {}
        self.__waiting_for_response: dict[str, Future] = {}

    async def start(self):
        self._consumer = AIOKafkaConsumer(self.__name)
        self._producer = AIOKafkaProducer()
        await self._consumer.start()
        await self._producer.start()
        self.__poll_task = self.__loop.create_task(self.__poll())

    async def stop(self):
        if self._consumer:
            await self._consumer.stop()
        if self._producer:
            await self._producer.stop()
        if self.__poll_task and not self.__poll_task.done():
            self.__poll_task.cancel()

    async def __poll(self):
        try:
            async for message in self._consumer:
                try:
                    data = orjson.loads(message.value)
                    await self.__on_message(data)
                except orjson.JSONDecodeError:
                    logger.error(f"Неизвестные данные: {message}")
        except CancelledError:
            pass

    async def send_event(
        self,
        kafka_topic: str,
        event_name: str,
        wait_for_response: bool = False,
        response_timeout: float = 30.0,
        *args,
        **kwargs,
    ):
        id = str(uuid.uuid4())
        await self._producer.send_and_wait(
            kafka_topic,
            orjson.dumps(
                {
                    "type": "event",
                    "id": id,
                    "response": wait_for_response,
                    "from": self.__name,
                    "name": event_name,
                    "args": list(args),
                    "kwargs": kwargs,
                }
            ),
        )
        if wait_for_response:
            future = self.__loop.create_future()
            self.__waiting_for_response[id] = future
            done, _ = await asyncio.wait([future], timeout=response_timeout)
            if done:
                return tuple(done)[0].result()
            else:
                self.__waiting_for_response[id].cancel()
                del self.__waiting_for_response[id]
        return None

    def event(self, name: str = None):
        def wrapper(func):
            self.__events[name] = func

        if isfunction(name):
            func = name
            name = func.__name__
            return wrapper(func)
        return wrapper

    def wrap_class(self, _class):
        def wrapper(*args, **kwargs):
            self.__class_instance = _class(*args, **kwargs)
            return self.__class_instance

        return wrapper

    async def __on_message(self, data: dict):
        if "type" not in data or data["type"] not in ("event", "response"):
            logger.error(f"Неправильные данные: {data}")
            return
        if data["type"] == "event":
            await self.__on_event(data)
        else:
            await self.__on_response(data)

    async def __on_event(self, data: dict):
        if not all(
            key in data for key in ("name", "id", "response", "from", "args", "kwargs")
        ):
            logger.error(f"Неправильные данные: {data}")
            return
        func = self.__events.get(data["name"], None)
        if func is None:
            logger.error(f"Неизвестное событие: {data['name']}.")
            return
        if iscoroutinefunction(func):
            result = await func(self.__class_instance, *data["args"], **data["kwargs"])
        else:
            result = func(self.__class_instance, *data["args"], **data["kwargs"])
        if data["response"]:
            await self._producer.send_and_wait(
                data["from"],
                orjson.dumps(
                    {"type": "response", "id": data["id"], "response": result}
                ),
            )

    async def __on_response(self, data: dict):
        if not all(key in data for key in ("id", "response")):
            logger.error(f"Неправильные данные: {data}")
            return
        future = self.__waiting_for_response.pop(data["id"], None)
        if future is None:
            logger.error(f"Неверное ID ответа: {data['id']}")
            return
        future.set_result(data["response"])


if __name__ == "__main__":
    import asyncio

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    client = Client("client", loop)

    @client.wrap_class
    class Test:
        @client.event
        async def test(self):
            print("Func is called")
            await asyncio.sleep(5)
            return "Hello world"

    async def main():
        await client.start()
        response = await client.send_event(
            "client", "test", wait_for_response=True, response_timeout=6.0
        )
        print(response)

    try:
        loop.create_task(main())
        loop.run_forever()
    except KeyboardInterrupt:
        loop.run_until_complete(client.stop())
        loop.stop()
