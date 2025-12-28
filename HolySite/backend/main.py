import secrets

from authentication.token import set_token_cookie, verify_session
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response
from routes import routes
from sessions import client

load_dotenv(".env")


async def lifespan(app: FastAPI):
    await client.start()
    yield
    await client.stop()


app = FastAPI(lifespan=lifespan)


for route in routes:
    app.include_router(route)
