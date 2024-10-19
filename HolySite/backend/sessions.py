import asyncio

from motor.motor_asyncio import AsyncIOMotorClient
from kafkaclient import Client

db = AsyncIOMotorClient()
client = Client("website", asyncio.get_event_loop())
