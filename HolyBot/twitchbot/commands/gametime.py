from typing import TYPE_CHECKING
from inspect import iscoroutinefunction
import time

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
    if any(args):
        return None
    if channel["is_live"]:
        played_time = channel["played_time"][channel["category"]] if channel["category"] in channel["played_time"] else 0
        return f'{channel["category"]} [{time.strftime("%H:%M:%S", time.gmtime(time.time() - channel["game_time"] + played_time))}]'
    else:
        return command.get("offline", "стрим офлайн")
    

NAME = "gametime"
INFO = {"name": NAME, "description": "GAMETIME"}
COROUTINE = iscoroutinefunction(command)
