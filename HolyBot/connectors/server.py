import asyncio
import sys
from random import randint

import uvloop
import orjson
from loguru import logger

logger.remove()
logger.add(sys.stdout, level="TRACE", enqueue=True)


class Server:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.connections: dict[str, asyncio.StreamWriter] = {}

    async def handle_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        try:
            while True:
                message = await reader.readline()
                if not message:
                    break
                received_json: dict = orjson.loads(message)
                logger.trace(received_json)
                if "to" in received_json:
                    names = received_json["to"]
                    if isinstance(names, str):
                        names = [names]
                    for name in names:
                        name = name.lower()
                        if name in self.connections:
                            logger.trace(
                                f"{connection_name} > {name}: {received_json.get('data', 'None')}"
                            )
                            del received_json["to"]
                            received_json["from"] = connection_name
                            self.connections[name].write(
                                orjson.dumps(received_json) + b"\n"
                            )
                            await writer.drain()
                        else:
                            logger.error(f"Неизвестное имя: {name}")
                else:
                    connection_name = received_json["name"].lower()
                    while connection_name in self.connections:
                        logger.warning(f"{connection_name} уже подключен, добавляю рандомное число")
                        connection_name += str(randint(0, 10000))
                    logger.info(f"Подключился клиент с именем {connection_name}")
                    self.connections[connection_name] = writer
        finally:
            logger.info(f"Клиент {connection_name} отключился")
            self.connections.pop(connection_name)
            writer.close()

    def start_server(self):
        async def start():
            try:
                server = await asyncio.start_server(
                    self.handle_client, self.host, self.port
                )
                async with server:
                    await server.serve_forever()
            except OSError as e:
                logger.exception(e)
                loop.stop()
            except Exception as e:
                logger.exception(e)

        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.create_task(start())

        def exception_handler(_, context):
            print(context)

        loop.set_exception_handler(exception_handler)
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            loop.stop()
