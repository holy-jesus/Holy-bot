import asyncio
import os

from motor.motor_asyncio import AsyncIOMotorClient
from kafkaclient import Client

db = AsyncIOMotorClient(
    username=os.getenv("mongodb_username"), password=os.getenv("mongodb_password")
)
client = Client("website", asyncio.get_event_loop())
