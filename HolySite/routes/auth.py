from uuid import uuid4

from fastapi import APIRouter, Request, Response
from fastapi.responses import RedirectResponse

from utils import SCOPES, client, create_token, logged_in, db

auth = APIRouter()


@auth.get("/login")
async def login(
    request: Request,
    response: Response,
    state: str,
    code: str = None,
    scope: str = None,
    error: str = None,
    error_description: str = None,
):
    if code and scope == SCOPES and state == request.cookies.get("state"):
        response = RedirectResponse("/profile")
        data = await client.send_event(
            to="twitchapi",
            event="user_logged_in",
            data={"code": code},
            wait_for_answer=True,
            timeout=10,
        )
        if not data:
            return RedirectResponse("/")
        user = (
            await db.users.find_one({"_id": data["id"], "login": data["login"]}) or {"bot_enabled": False, "prefix": "!"}
        )
        access_token = {
            "_id": data["id"],
            "access_token": data["access_token"],
            "expires": data["expires"],
            "refresh_token": data["refresh_token"],
        }
        await db.tokens.update_one({"_id": data["id"]}, {"$set": access_token}, upsert=True)
        session_id, token = await create_token()
        user["_id"] = data["id"]
        user["login"] = data["login"]
        user["session_id"] = session_id
        await db.users.update_one({"_id": data["id"]}, {"$set": user}, upsert=True)
        response.set_cookie("token", token)
        response.delete_cookie("state")
        return response
    elif error and error_description:
        return RedirectResponse("/")  # TODO
    else:
        return RedirectResponse("/")


@auth.get("/logout")
@logged_in(False, False)
async def logout(request: Request, response: Response, user=None):
    response.delete_cookie("token")
    response.status_code = 302
    response.headers["location"] = "/"
    if user:
        await db.users.update_one({"_id": user["_id"]}, {"$set": {"session_id": None}})
        return response
    else:
        return response
