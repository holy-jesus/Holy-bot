from typing import TYPE_CHECKING
from inspect import iscoroutinefunction

if TYPE_CHECKING:
    from twitchbot.holybot import HolyBot


def command(
    channel: dict,
    command: dict,
    parsed: dict,
    args: tuple,
    running_commands: dict,
    ping_name: str,
    bot: "HolyBot",
):
    if not any(args):
        return channel["title"]

NAME = "title"
INFO = {"name": NAME, "description": "TITLE"}
COROUTINE = iscoroutinefunction(command)
