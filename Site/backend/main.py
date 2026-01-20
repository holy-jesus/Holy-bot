import secrets
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from routes import routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)


for route in routes:
    app.include_router(route)
