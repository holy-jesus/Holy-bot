from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    email: str
    password: str | None


class UserLoginWithPassword(BaseModel):
    username: str
    password: str


class UserLoginWithEmail(BaseModel):
    email: str
