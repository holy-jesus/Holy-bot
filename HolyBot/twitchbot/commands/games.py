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
    if channel["is_live"]:
        if channel["played_time"]:
            games = ""
            for game, gametime in channel["played_time"].items():
                played_time = gametime
                if game == channel["category"]:
                    played_time += time.time() - channel["game_time"]
                if played_time < 60:
                    continue
                games += f'{game} [{time.strftime("%H:%M:%S", time.gmtime(played_time))}] | '
            if channel["category"] not in channel["played_time"]:
                games += f'{channel["category"]} [{time.strftime("%H:%M:%S", time.gmtime(time.time() - channel["game_time"]))}] | '
            games = games[:-3]
        else:
            games = f'{channel["category"]} [{time.strftime("%H:%M:%S", time.gmtime(time.time() - channel["game_time"]))}]'
        return games + "."
    else:
        return command.get("offline", "стрим офлайн")


NAME = "games"
INFO = {"name": NAME, "description": "GAMES", "only_live": True}
COROUTINE = iscoroutinefunction(command)




NAME = "games"
INFO = {"name": NAME, "description": "GAMES"}
COROUTINE = iscoroutinefunction(command)
