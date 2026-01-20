from fastapi import APIRouter

from holybot_shared.models import User
from ..models import UserCreate, UserLoginWithEmail, UserLoginWithPassword

authentication = APIRouter()


@authentication.post("/register")
async def register_user(user: UserCreate):
    pass


@authentication.post("/login")
async def login_user(user: UserLoginWithPassword):
    pass


@authentication.post("/login-email")
async def login_user_with_email(email: UserLoginWithEmail):
    pass
