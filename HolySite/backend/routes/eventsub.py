from fastapi import APIRouter
from bson import ObjectId

eventsub = APIRouter(prefix="/eventsub")


@eventsub.get("/{id}")
async def main(id: str):
    pass
