import importlib
from glob import glob
from string import Template
from time import time
from typing import TYPE_CHECKING
from asyncio import to_thread

if TYPE_CHECKING:
    from twitchbot.holybot import HolyBot

FILES_TO_IGNORE = ("__init__.py", "commands.py")
PATH = "/".join(__file__.split("/")[:-1])
IDENTIFIERS = {}
for file in glob(PATH + "/*.*"):
    file = file.split("/")[-1]
    if file in FILES_TO_IGNORE or not file.endswith(".py"):
        continue
    module = importlib.import_module(
        f"twitchbot.commands.{file.replace('.py', '')}",
    )
    IDENTIFIERS[module.NAME] = {"func": module.command, "coroutine": module.COROUTINE}


class Commands:
    def __init__(self, bot: "HolyBot") -> None:
        self.bot = bot
        self.db = bot.db
        self.client = bot.client

        self._identifiers = IDENTIFIERS
        self._commands = {}
        self._running_commands = {}

        # self.client.event("update")(self.update)
        self.bot.loop.create_task(self._async_init())

    async def update(self, command: dict):
        self._commands

    async def _async_init(self):
        async for command in self.db.commands.find():
            if command["user_id"] not in self._commands:
                self._commands[command["user_id"]] = {}
            for alias in command["aliases"]:
                self._commands[command["user_id"]][alias] = command

    def get_command(self, command: str, user_id: str):
        return self._commands.get(user_id, {}).get(command)

    async def execute_command(self, parsed: dict):
        text = parsed["text"]
        channel = await self.db.users.find_one({"_id": parsed["room-id"]})
        if not text.startswith(channel["prefix"]):
            return
        text = text.replace(channel["prefix"], "", 1).strip()
        args = text.split()
        if not args:
            return
        command = args[0].lower()
        command_dict = await self.db.commands.find_one(
            {"aliases": command, "user_id": parsed["room-id"]}
        )
        if not command_dict:
            return
        text = text.replace(command, "", 1).strip()
        command = command_dict["aliases"][0]
        args = args[1:]
        command_name = f"{parsed['room-id']}:{command}"
        if isinstance(command_dict["cooldown"], dict):
            channel_cd = command_dict["cooldown"]["global"]
            user_cd = command_dict["cooldown"]["user"]
        else:
            user_cd = channel_cd = command_dict["cooldown"]
        timestamp = time()
        cooldown = await self.db.cooldowns.find_one({"_id": command_dict["_id"]}) or {}
        if (
            parsed["user-id"] != channel["_id"]
            and not parsed.get("mod", False)
            and (
                cooldown.get(parsed["user-id"], 0) > timestamp
                or cooldown.get("channel", 0) > timestamp
            )
        ):
            return
        if command_name in self._running_commands:
            self._running_commands[command_name] += f", @{parsed['login']}"
            return
        self._running_commands[command_name] = f"@{parsed['login']}"
        template = Template(command_dict["response"])
        mapped = {}
        identifiers = tuple(map(str.lower, template.get_identifiers()))
        for identifier in identifiers:
            if identifier == "ping":
                continue
            identifier_dict = self._identifiers.get(identifier, None)
            if not identifier_dict:
                continue
            elif identifier_dict["coroutine"]:
                value = await identifier_dict["func"](
                    channel, command_dict, parsed, args, self._running_commands, command_name, self.bot
                )
            else:
                value = identifier_dict["func"](
                    channel,
                    command_dict,
                    parsed,
                    args,
                    self._running_commands,
                    command_name,
                    self.bot,
                )
            if not value:
                await self.db.cooldowns.update_one(
                    {"_id": command_dict["_id"]},
                    {
                        "$set": {
                            "channel": channel_cd + timestamp,
                            parsed["user-id"]: user_cd + timestamp,
                        }
                    },
                    upsert=True,
                )
                self._running_commands.pop(command_name, None)
                return
            mapped[identifier] = value
        if "ping" in identifiers:
            # Снизу чтобы если условный ${music} занял какое-то время,
            # то все кто активировали команду попали в ${ping}
            mapped["ping"] = self._identifiers["ping"]["func"](
                channel, command_dict, parsed, args, self._running_commands, command_name, self.bot
            )
        response = template.safe_substitute(mapped)
        await self.bot.send_chat_message(response, channel["login"])
        timestamp = time()
        await self.db.cooldowns.update_one(
            {"_id": command_dict["_id"]},
            {
                "$set": {
                    "channel": channel_cd + timestamp,
                    parsed["user-id"]: user_cd + timestamp,
                }
            },
            upsert=True,
        )
        self._running_commands.pop(command_name, None)


"""
Для кулдауна использовать либо базу данных, либо 
"""
