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
    return channel["login"]


NAME = "channel_name"
INFO = {"name": NAME, "description": "CHANNEL NAME"}
COROUTINE = iscoroutinefunction(command)
