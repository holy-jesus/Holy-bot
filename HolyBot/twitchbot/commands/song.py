from typing import TYPE_CHECKING
from inspect import iscoroutinefunction

if TYPE_CHECKING:
    from twitchbot.holybot import HolyBot


async def command(
    channel: dict,
    command: dict,
    parsed: dict,
    args: tuple,
    running_commands: dict,
    ping_name: str,
    bot: "HolyBot",
):
    if channel["is_live"]:
        
        song = await bot.client.send_event(
            "recognizer", "recognize", {"login": channel["login"]}, True
        )
        return command.get(song, {"none": "не распознал :(", "error": "что-то сломалось :("}.get(song, song))
    else:
        return command.get("offline", "стрим офлайн")


NAME = "song"
INFO = {"name": NAME, "description": "SONG"}
COROUTINE = iscoroutinefunction(command)
