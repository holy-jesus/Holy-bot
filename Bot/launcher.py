import asyncio
import os
import signal
from time import time
import sys

from connectors import Client


async def connect_stdin_stdout():
    loop = asyncio.get_event_loop()
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)
    w_transport, w_protocol = await loop.connect_write_pipe(
        asyncio.streams.FlowControlMixin, sys.stdout
    )
    writer = asyncio.StreamWriter(w_transport, w_protocol, reader, loop)
    return reader, writer


FILES = {
    "Server": {"file": "run_server.py", "running": False, "task": None, "proc": None},
    "TwitchApi": {
        "file": "run_twitch_api.py",
        "running": False,
        "task": None,
        "proc": None,
    },
    "Recognizer": {
        "file": "run_recognizer.py",
        "running": False,
        "task": None,
        "proc": None,
    },
    "TwitchBot": {
        "file": "run_twitch_bot.py",
        "running": False,
        "task": None,
        "proc": None,
    },
}

PATH_TO_PYTHON = os.getcwd() + "/../venv/bin/python"
CURRENT_PATH = os.getcwd() + "/"


class Launcher:
    client = Client(name="launcher", host="localhost", port=42069)

    def __init__(self) -> None:
        self.client.instance_of_class = self
        self.loop = asyncio.new_event_loop()
        self.task = None
        asyncio.set_event_loop(self.loop)

    async def main(self):
        reader, writer = await connect_stdin_stdout()

        async def print(text: str, end: str = b"\n"):
            if not end:
                end = end.encode()
            writer.write(text.encode() + end)
            await writer.drain()

        async def input(text: str):
            await print(text, end="")
            return (await reader.readline()).decode("utf-8").replace("\n", "")

        while True:
            try:
                i = 0
                for key, value in FILES.items():
                    i += 1
                    await print(
                        f"{i}. {key}: {'Running' if value['running'] else 'Not Running'}"
                    )
                await print("5. Run all.")

                choice = await input(">>> ")
                if choice in ["q", "exit"]:
                    for value in list(FILES.values())[::-1]:
                        if value["running"]:
                            value["task"].cancel()
                            await asyncio.sleep(0.2)
                    break
                elif choice in ["1", "2", "3", "4"]:
                    program = list(FILES.values())[int(choice) - 1]
                    name = list(FILES.keys())[int(choice) - 1]
                    if not program["running"]:
                        task = self.loop.create_task(self.thread(name, program))
                        program["task"] = task
                        program["running"] = True
                    else:
                        program["task"].cancel()
                        program["running"] = False
                elif choice in ["5", "all"]:
                    for name, program in FILES.items():
                        if program["running"]:
                            continue
                        task = self.loop.create_task(self.thread(name, program))
                        program["task"] = task
                        program["running"] = True
                        await asyncio.sleep(1)
            except asyncio.CancelledError:
                await print("Main function was cancelled.")
                for value in list(FILES.values())[::-1]:
                    if value["running"]:
                        value["task"].cancel()
                        await asyncio.sleep(0.25)
                break
        self.loop.stop()

    async def thread(self, name, program):
        errors = []
        try:
            while True:
                cmd = PATH_TO_PYTHON + " " + CURRENT_PATH + program["file"]
                cmd = cmd.split()
                proc = await asyncio.create_subprocess_exec(*cmd)
                program["proc"] = proc
                future = asyncio.ensure_future(proc.communicate())
                await asyncio.wait([future])
                print(f"{name} exited with code {proc.returncode}\nRestarting...")
                errors.append(int(time()))
                for error in errors:
                    if int(time()) - error > 30:
                        errors.remove(error)
                if len(errors) > 5:
                    program["running"] = False
                    program["task"] = None
                    program["proc"] = None
                    break
        except asyncio.CancelledError:
            print(f"{name} thread was cancelled")
            proc.terminate()
            done, pending = await asyncio.wait([future], timeout=1)
            if pending:
                if proc.returncode is None:
                    try:
                        proc.kill()
                    except ProcessLookupError:
                        pass
            program["running"] = False
            program["task"] = None
            program["proc"] = None

    def start(self):
        self.task = self.loop.create_task(self.main())
        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            self.loop.run_until_complete(self.close())

    async def close(self):
        if self.task:
            self.task.cancel()


if __name__ == "__main__":
    launcher = Launcher()
    launcher.start()
