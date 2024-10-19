from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from path import get_frontend
from sessions import client
from routes import routes


frontend_path, index_path, assets_path = get_frontend()


async def lifespan(app: FastAPI):
    await client.start()
    yield
    await client.stop()


app = FastAPI(lifespan=lifespan)


@app.middleware("http")
async def update_token(request: Request, call_next):
    # Здесь получится только обновлять токен, потому что call_next принимает только request
    response: Response = await call_next(request)
    return response


app.mount("/assets", StaticFiles(directory=assets_path), name="assets")
for route in routes:
    app.include_router(route)


@app.get("/")
async def index(request: Request):
    return HTMLResponse(index_path.read_text("utf-8"))
