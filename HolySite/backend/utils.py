import os
from time import time
from functools import wraps
from uuid import uuid4
import sys

from dotenv import load_dotenv
from fastapi import Request, Response
from fastapi.responses import RedirectResponse
from jose import JWTError, jwt
from fastapi.templating import Jinja2Templates
from motor.motor_asyncio import AsyncIOMotorClient
from loguru import logger

from holy_bot.HolyBot.connectors import Client

load_dotenv(".env")

logger.remove()
logger.add("holysite.log", level="DEBUG", enqueue=True)
# logger.add(sys.stderr, level="DEBUG", enqueue=True)


SECRET = os.getenv("eventsub_secret")
ALGORITHM = "HS256"
EXPIRES_AFTER = 30 * 60
SCOPES = ""
BASE_PATH = os.getcwd()
TEMPLATES_PATH = BASE_PATH + "/static/html/"
DEFAULT_COMMANDS = []


client = Client(name=f"website{os.getpid()}", host="localhost", port=42069)
templates = Jinja2Templates(directory="templates")
db = AsyncIOMotorClient(os.getenv("mongodb_link"), connect=False)["holy_bot"]


def logged_in(only_logged_in=True, refresh_token=True):
    def wrapper(func):
        @wraps(func)
        async def wrapped(*args, **kwargs):
            request: Request = kwargs.get("request")
            response: Response = kwargs.get("response")
            response.status_code = 200
            token = request.cookies.get("token")
            if not token and only_logged_in:
                return RedirectResponse("/")
            elif not token:
                kwargs["user"] = None
                return await func(*args, **kwargs)
            try:
                payload = jwt.decode(
                    token, SECRET, algorithms=[ALGORITHM], options={"verify_exp": False}
                )
                session_id: str = payload.get("session_id")
                expires: float = payload.get("exp")
                user = await db.users.find_one({"session_id": session_id})
                kwargs["user"] = user
                if not user:
                    response = RedirectResponse("/")
                    response.delete_cookie("token")
                    return response
                elif time() > expires and refresh_token:
                    session_id, token = await create_token()
                    response.set_cookie("token", token)
                    await db.users.update_one(
                        {"_id": user["_id"]}, {"$set": {"session_id": session_id}}
                    )
                return await func(*args, **kwargs)
            except JWTError:
                response = RedirectResponse("/")
                response.delete_cookie("token")
                return response

        return wrapped

    if callable(only_logged_in):
        func = only_logged_in
        only_logged_in = True
        return wrapper(func)
    else:
        return wrapper


async def create_token() -> tuple[str, str]:
    session_id = str(uuid4())
    while (await db.users.find_one({"session_id": session_id})) is not None:
        session_id = str(uuid4())
    to_encode = {"session_id": session_id, "exp": time() + EXPIRES_AFTER}
    encoded_jwt = jwt.encode(to_encode, SECRET, algorithm=ALGORITHM)
    return session_id, encoded_jwt
