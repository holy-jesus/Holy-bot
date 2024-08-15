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
    return running_commands.pop(ping_name)


NAME = "ping"
INFO = {"name": NAME, "description": "PING"}
COROUTINE = iscoroutinefunction(command)
