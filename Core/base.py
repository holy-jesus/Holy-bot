from abc import ABC, abstractmethod


class Event(ABC):
    name: str

    @abstractmethod
    async def handle(self, payload: dict) -> None:
        pass
