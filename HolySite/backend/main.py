from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import secrets

from frontend_handler import assets_path, get_frontend
from sessions import client
from routes import routes
from token_handler import verify_session, set_token_cookie

load_dotenv(".env")


async def lifespan(app: FastAPI):
    await client.start()
    yield
    await client.stop()


app = FastAPI(lifespan=lifespan)


@app.middleware("http")
async def update_token(request: Request, call_next):
    response: Response = await call_next(request)
    token = request.cookies.get("token")
    if token:
        session = await verify_session(token)
        if session is None:
            response.delete_cookie("token")
        elif session is True:
            pass
        else:
            set_token_cookie(response, session)
    return response


app.mount("/assets", StaticFiles(directory=assets_path), name="assets")
for route in routes:
    app.include_router(route)


@app.get("/")
def index(request: Request):
    response = get_frontend()
    response.set_cookie("state", secrets.token_hex(16), secure=True, samesite="lax")
    return response
