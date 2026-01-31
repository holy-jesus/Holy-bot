from fastapi import APIRouter

from services.auth.middlewares import AdminOnly

twitch = APIRouter(prefix="/twitch", route_class=AdminOnly)
