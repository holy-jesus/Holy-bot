import asyncio
from asyncio import BaseEventLoop
from inspect import iscoroutinefunction, isfunction
from typing import Callable

import nats
import orjson
from loguru import logger
from nats.aio.client import Client as NATSClient
from nats.aio.msg import Msg
from nats.errors import TimeoutError as NatsTimeoutError


class Client:
    def __init__(
        self, name: str, loop: BaseEventLoop, nats_url: str = "nats://localhost:4222"
    ) -> None:
        self.__name: str = name
        self.__loop: BaseEventLoop = loop
        self.__nats_url: str = nats_url
        self.__class_instance: object = None
        self._nc: NATSClient | None = None
        self.__events: dict[str, Callable] = {}
        # Словари для ожидания ответов (futures) больше не нужны, NATS берет это на себя

    async def start(self):
        # Подключение к NATS
        self._nc = await nats.connect(self.__nats_url, loop=self.__loop)

        # Подписка на топик (Subject) равный имени клиента.
        # queue=self.__name обеспечивает Load Balancing (аналог Consumer Group в Kafka).
        await self._nc.subscribe(
            self.__name, cb=self.__nats_callback, queue=self.__name
        )
        logger.info(
            f"Client {self.__name} started and listening on subject '{self.__name}'"
        )

    async def stop(self):
        if self._nc:
            await self._nc.drain()  # Ждем обработки последних сообщений
            await self._nc.close()

    async def __nats_callback(self, msg: Msg):
        """Callback функция, вызываемая NATS при получении сообщения"""
        try:
            data = orjson.loads(msg.data)
            # Передаем само сообщение msg, чтобы можно было ответить через msg.respond
            await self.__on_message(data, msg)
        except orjson.JSONDecodeError:
            logger.error(f"Неизвестные данные: {msg.data}")
        except Exception as e:
            logger.exception(e)

    async def send_event(
        self,
        topic: str,  # В терминах NATS это Subject, но оставим имя аргумента
        event_name: str,
        wait_for_response: bool = False,
        response_timeout: float = 30.0,
        *args,
        **kwargs,
    ):
        payload = orjson.dumps(
            {
                "type": "event",
                "from": self.__name,
                "name": event_name,
                "args": list(args),
                "kwargs": kwargs,
            }
        )

        try:
            if wait_for_response:
                # NATS Native Request-Reply
                # Мы просто ждем ответа, NATS сам создает уникальный inbox для ответа
                response_msg = await self._nc.request(
                    topic, payload, timeout=response_timeout
                )

                # Декодируем ответ
                response_data = orjson.loads(response_msg.data)

                # В старой логике ответ был обернут. Если вы сохраняете структуру:
                if isinstance(response_data, dict) and "response" in response_data:
                    return response_data["response"]
                return response_data
            else:
                # Fire and Forget (просто публикация)
                await self._nc.publish(topic, payload)
                return None
        except NatsTimeoutError:
            logger.error(
                f"Timeout waiting for response from {topic} (event: {event_name})"
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

    async def __on_message(self, data: dict, msg: Msg):
        if "type" not in data or data["type"] != "event":
            # Обработку type="response" убрали, так как send_event теперь ждет ответ линейно
            logger.error(f"Неправильные данные или тип: {data}")
            return

        await self.__on_event(data, msg)

    async def __on_event(self, data: dict, msg: Msg):
        # Проверка ключей (id и response больше не обязательны в payload, так как это свойства протокола NATS)
        if not all(key in data for key in ("name", "from", "args", "kwargs")):
            logger.error(f"Неполные данные события: {data}")
            return

        func = self.__events.get(data["name"], None)
        if func is None:
            logger.error(f"Неизвестное событие: {data['name']}.")
            return

        # Выполнение функции
        try:
            if iscoroutinefunction(func):
                result = await func(
                    self.__class_instance, *data["args"], **data["kwargs"]
                )
            else:
                result = func(self.__class_instance, *data["args"], **data["kwargs"])
        except Exception as e:
            logger.exception(f"Error executing event {data['name']}")
            result = None

        # Если у сообщения есть reply subject (то есть отправитель сделал request), отправляем ответ
        if msg.reply:
            response_payload = orjson.dumps({"type": "response", "response": result})
            await self._nc.publish(msg.reply, response_payload)


if __name__ == "__main__":
    # Пример использования
    # Для теста нужен запущенный NATS сервер (nats-server)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Создаем два клиента для имитации общения
    server = Client("recognizer", loop)
    client = Client("client", loop)

    # Регистрируем обработчик на "сервере"
    @server.event("recognize")
    async def recognize_handler(inst, login):
        print(f"[Server] Processing recognize for {login}...")
        await asyncio.sleep(1)  # Имитация работы
        return f"User {login} recognized!"

    async def main():
        await server.start()
        await client.start()

        print("[Client] Sending request...")
        # wait_for_response=True использует NATS Request
        response = await client.send_event(
            "recognizer", "recognize", login="hoiy_jesus", wait_for_response=True
        )
        print(f"[Client] Got response: {response}")

        # wait_for_response=False использует NATS Publish
        print("[Client] Sending fire-and-forget...")
        await client.send_event(
            "recognizer", "recognize", login="silent_user", wait_for_response=False
        )

    try:
        loop.run_until_complete(main())
        # Небольшая пауза, чтобы успел обработаться fire-and-forget
        loop.run_until_complete(asyncio.sleep(0.5))
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(client.stop())
        loop.run_until_complete(server.stop())
        loop.stop()
