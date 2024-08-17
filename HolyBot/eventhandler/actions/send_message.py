from base import BaseAction

class SendMessage(BaseAction):
    type = "send_message"
    value = "value"

    async def execute(self, data: dict):
        pass