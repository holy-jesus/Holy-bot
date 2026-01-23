import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_DOMAIN")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


for route in routes:
    app.include_router(route)


@app.get("/health")
async def health():
    return {"status": "ok"}
