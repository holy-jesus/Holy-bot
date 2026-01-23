import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
import valkey.asyncio as valkey

from .routes import routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.valkey = valkey.Valkey(
        host=os.getenv("VALKEY_HOST", "valkey"),
        port=int(os.getenv("VALKEY_PORT", "6379")),
    )
    yield
    await app.state.valkey.aclose()


app = FastAPI(lifespan=lifespan)


for route in routes:
    app.include_router(route)


@app.get("/health")
async def health():
    return {"status": "ok"}
