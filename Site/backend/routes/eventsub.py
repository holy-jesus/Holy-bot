from fastapi import APIRouter

eventsub = APIRouter(prefix="/eventsub")


@eventsub.get("/{id}")
async def main(id: str):
    pass
