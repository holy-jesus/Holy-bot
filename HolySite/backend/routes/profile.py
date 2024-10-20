from fastapi import APIRouter, Request

from frontend_handler import get_frontend

profile = APIRouter()

@profile.get("/profile")
async def profile_page():
    return get_frontend()
