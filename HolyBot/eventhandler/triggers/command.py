from .base import BaseTrigger

class Command(BaseTrigger):
    type = "command"

    def get(data: dict) -> dict | None:
        pass
