from typing import overload, TYPE_CHECKING
import asyncio


if TYPE_CHECKING:
    from twitchbot.holybot import HolyBot
    from motor import core


class Channels:
    def __init__(self, bot: "HolyBot") -> None:
        self.bot = bot
        self.db: "core.Collection" = bot.db.users
        self.loop = bot.loop
        self._statuses: dict[str, asyncio.Future] = {}
        self._channels_by_id: dict[str, dict] = {}
        self._channels_by_login: dict[str, dict] = {}
        self._channels: list[dict] = []
        self.loop.create_task(self._async_init())

    def __iter__(self):
        return self._channels.__iter__()

    async def _async_init(self):
        async for user in self.db.find({"bot_enabled": True}):
            if user not in self._channels:
                self._channels.append(user)
            self._channels_by_id[user["_id"]] = user
            self._channels_by_login[user["login"]] = user

    async def join_all_channels(self):
        for i in range(len(self._channels))[::20]:
            await self.bot.join_channels(logins=list(channel["login"] for channel in self._channels[i:i+20]), init=True)
            await asyncio.sleep(11.0)

    async def get_from_db(self, **kwargs) -> dict | None:
        if "id" in kwargs:
            kwargs["_id"] = kwargs.pop("id")
        user = await self.db.find_one(kwargs)
        if not user:
            return None
        if user not in self._channels:
            self._channels.append(user)
        self._channels_by_id[user["_id"]] = user
        self._channels_by_login[user["login"]] = user
        return user

    def init_statuses(self, logins: list[str]):
        for login in logins:
            self._statuses[login] = self.loop.create_future()

    def set_status(self, login: str, status: dict):
        if login in self._statuses:
            self._statuses[login].set_result(status)

    async def get_statuses(self, logins: list[str]):
        results = {}
        for login in logins:
            try:
                result = await asyncio.wait_for(self._statuses[login], timeout=5.0)
            except TimeoutError:
                result = {"success": False, "error": "timeout"}
            del self._statuses[login]
            results[login] = result
        return results

    def get(self, id: str = None, login: str = None) -> dict:
        if id and id in self._channels_by_id:
            return self._channels_by_id.get(id)
        elif login and login in self._channels_by_login:
            return self._channels_by_login.get(login)
        return None

    def pop(self, id: str = None, login: str = None) -> dict | None:
        user = None
        if id:
            user = self._channels_by_id.get(id, None)
        elif login:
            user = self._channels_by_login.get(login, None)
        if not user:
            return None
        self._channels_by_id.pop(user["_id"], None)
        self._channels_by_login.pop(user["login"], None)
        if user in self._channels:
            self._channels.remove(user)
        return user
