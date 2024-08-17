from base import BaseTrigger
from command import Command

triggers = {"command": Command}

class Triggers:
    @staticmethod
    def get(type: str, data: dict):
        trigger = triggers.get(type, None)
        if not trigger:
            return None
        return trigger.get(data)