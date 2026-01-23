from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str | None


class UserLoginWithPassword(BaseModel):
    username: str
    password: str


class UserLoginWithEmail(BaseModel):
    email: EmailStr
