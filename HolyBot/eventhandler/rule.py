from HolyBot.eventhandler.triggers import Triggers
from HolyBot.eventhandler.actions import Actions

trigger = Triggers()
actions = Actions()

class Rule:
    async def get(channel_id: str, type: str, data: dict):  
        query = trigger.get(type, data)
        if not query:
            return
        await actions.get(query)
