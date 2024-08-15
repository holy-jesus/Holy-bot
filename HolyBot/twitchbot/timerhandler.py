from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import asyncio
    from twitchbot.holybot import HolyBot


class Timer:
    def __init__(self, bot: "HolyBot") -> None:
        self.bot = bot
        self.loop: "asyncio.AbstractEventLoop" = bot.loop
        self.db = bot.db
        self.client = bot.client
        self.timers: dict[str, "asyncio.TimerHandle"] = {}
        self.loop.create_task(self.start_from_db())
        self.client.event(self.start_from_db)
        self.client.event(self.disable_timer)


    def start_timer(self, timer: dict):
        self.timers[timer["_id"]] = self.loop.call_later(
            timer["cooldown"] * 60, self.callback, timer
        )

    async def start_from_db(self, **kwargs):
        async for timer in self.db.timers.find(kwargs):
            self.start_timer(timer)

    async def disable_timer(self, _id: str):
        self.timers[_id].cancel()
        del self.timers[_id]

    def callback(self, timer: dict):
        if timer["type"] == 0:
            self.loop.create_task(
                self.send_chat_message(timer["message"], timer["channel_id"])
            )
        else:
            self.loop.create_task(
                self.send_announcment(timer["message"], timer["channel_id"])
            )
        self.start_timer(timer)

    async def send_chat_message(self, text: str, id: str):
        await self.bot.send_chat_message_by_id(text, id=id)

    async def send_announcment(self, text: str, id: str):
        await self.bot.send_chat_announcement(text, id)


"""
Timers:
    _id: ...
    channel_id: ...
    message: text what to send
    offline_cooldown: minimum 5 min max 1440 min
    online_cooldown: minimum 5 min max 1440 min
"""
