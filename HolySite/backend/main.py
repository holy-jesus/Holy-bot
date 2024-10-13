from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from path import get_frontend


frontend_path, index_path, assets_path = get_frontend()

app = FastAPI()


app.mount("/assets", StaticFiles(directory=assets_path), name="assets")


@app.get("/")
async def index(request: Request):
    return HTMLResponse(index_path.read_text("utf-8"))
