from fastapi import APIRouter

auth = APIRouter()


@auth.get("/login")
async def login():
    pass


@auth.get("/logout")
async def logout():
    pass
