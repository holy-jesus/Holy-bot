from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse

from utils import logged_in, client, templates


commands = APIRouter(prefix="/commands")
"""
@commands.get("/")
async def commands_get(request: Request):
    return templates.TemplateResponse("commands.html", {"request": request})

"""