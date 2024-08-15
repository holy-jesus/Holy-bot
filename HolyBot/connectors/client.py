from inspect import signature, isfunction, _empty
from functools import partial
import asyncio

import orjson
from loguru import logger


class Client:
    def __init__(
        self, name: str, host: str, port: int, loop: asyncio.AbstractEventLoop = None
    ):
        self.name: str = name.lower()
        self.host: str = host
        self.port: int = port
        self.loop: asyncio.AbstractEventLoop = loop or asyncio.get_event_loop()
        self.reader: asyncio.StreamReader = None
        self.writer: asyncio.StreamWriter = None
        self.instance_of_class = None
        self.events: bool = {}
        self.waiting_for_answer: dict[str, asyncio.Future] = {}
        self.connected = asyncio.Event()

    def start(self) -> None:
        self.loop.create_task(self.connect())

    async def connect(self) -> bool:
        try:
            self.reader, self.writer = await asyncio.open_connection(
                self.host, self.port
            )
            self.connected.set()
            await self.send_message({"name": self.name})
            self.loop.create_task(self.thread())
            return True
        except ConnectionRefusedError:
            logger.error(
                "Не могу подключиться к серверу"
            )
            return False

    async def thread(self) -> None:
        try:
            while True:
                message = await self.reader.readline()
                if not message:
                    logger.warning("Подключение было закрыто")
                    break
                message = orjson.loads(message)
                logger.trace(f"< {message}")
                event = message.get("event")
                if event in self.waiting_for_answer:
                    data = message.get("data")
                    self.waiting_for_answer[event].set_result(data)
                elif event in self.events:
                    data = message.get("data")
                    sender = message.get("from")
                    answer = message.get("answer")
                    self.loop.create_task(self.task(sender, event, answer, data))
                else:
                    logger.error(f"Событие {event} не найдено")
        except Exception as e:
            logger.exception(e)
        finally:
            self.connected.clear()
            self.writer.close()

    async def send_message(self, message: dict, _retry: bool = False) -> None:
        if self.connected.is_set():
            logger.trace(f"> {message}")
            self.writer.write(orjson.dumps(message) + b"\n")
            await self.writer.drain()
        elif not _retry:
            await self.connect()
            await self.send_message(message, True)
        else:
            logger.error("Сервер офлайн, не могу отправить сообщение")

    async def send_event(
        self,
        to: str,
        event: str,
        data: dict | None,
        wait_for_answer: bool = False,
        timeout: float | int = None,
    ):
        event_id = len(self.waiting_for_answer)
        message = {
            "to": to,
            "event": event,
            "data": data,
        }
        if wait_for_answer:
            message["answer"] = event_id
        await self.send_message(message)
        if wait_for_answer:
            self.waiting_for_answer[event_id] = self.loop.create_future()
            try:
                await asyncio.wait_for(
                    self.waiting_for_answer[event_id], timeout=timeout
                )
            except TimeoutError:
                del self.waiting_for_answer[event_id]
                return None
            else:
                result = self.waiting_for_answer[event_id].result()
                del self.waiting_for_answer[event_id]
                return result

    def event(self, name: str = None):
        def wrapper(func):
            if name is None or name == func:
                self.events[func.__name__] = func
            else:
                self.events[name] = func
            return func

        if isfunction(name):
            return wrapper(name)
        return wrapper

    def prepare_func(self, data: dict | list | str | int, func, cls) -> dict | None:
        """
        А если нам надо передать в аргумент сам лист? Проверять по typing? Или по количеству аргументов?
        (Если функция принимает 1 аргумент, тогда передавать лист/словарь в изначальном виде).
        Щас мне кажется лучшим вариантом словарь всегда распаковывать, кроме тех случаев, когда принимающий аргумент всего 1
        а в словаре есть ещё поля. Просто если словарь пришёл с 1 ключём и аргумент принимает этот ключ, будет не круто пихать туда словарь.
        А также что делать с неиспользованными/лишними аргументами? Игнорить?
        """
        takes_args = dict(signature(func).parameters)
        if not takes_args:
            return func
        args = []
        kwargs = {}
        if "self" in takes_args and self.instance_of_class:
            kwargs["self"] = cls
            del takes_args["self"]
        elif "self" in takes_args:
            logger.error("Не указан self")
            return None
        necessary_args = {
            name: param for name, param in takes_args.items() if param.default is _empty
        }
        if isinstance(data, (str, int)) or data is None:
            if len(necessary_args) > 1:
                return None
            kwargs[tuple(takes_args.keys())[0]] = data
        elif isinstance(data, (list, tuple)):
            if len(necessary_args) > len(data):
                return None
            elif len(data) > len(takes_args) and len(takes_args) == 1:
                kwargs[tuple(takes_args.keys())[0]] = data
            else:
                for name, value in zip(takes_args, data):
                    kwargs[name] = value
        elif isinstance(data, dict):
            for name in takes_args:
                empty = name in necessary_args
                if name in data:
                    kwargs[name] = data[name]
                elif empty and name not in data:
                    logger.warning(f"name={name}\nempty={empty}\ntakes_args={takes_args}\nnecessary_args={necessary_args}\ndata={data}")
                    # Значит на обязательный параметр в функции у нас нету значения
                    return None
        return partial(func, *args, **kwargs)

    async def task(
        self, sender: str, event: str, answer: int | None, data: dict | None
    ):
        async def wrapper(func):
            try:
                return await func()
            except Exception as e:
                logger.exception(e)
                raise
        func = self.prepare_func(data, self.events[event], self.instance_of_class)
        if func is None:
            logger.error("Function is None!")
            return
        result = await wrapper(func)
        if answer is not None:
            await self.send_event(sender, answer, result)
