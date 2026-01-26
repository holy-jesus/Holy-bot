import asyncio
import json


class Core:
    def __init__(self, loop: asyncio.AbstractEventLoop = None):
        self.loop = loop or asyncio.get_event_loop()

    async def start(self):
        pass

    def run(self):
        self.loop.create_task(self.start())
        self.loop.run_forever()

    def stop(self):
        self.loop.stop()
