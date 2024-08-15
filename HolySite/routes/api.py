from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse

from utils import logged_in, client, templates, db


api = APIRouter(prefix="/api")


# @api.post("/api/bot/enable")
# @logged_in
# async def enable_bot(request: Request, response: Response, user=None):
#     if not user["bot_enabled"]:
#         result = await client.send_event(
#             to="twitchbot",
#             event="channel_connected",
#             data={"ids": [user["_id"]]},
#             wait_for_answer=True,
#             timeout=5,
#         )
#         if not result:
#             result = {"success": True, "error": "botnotenabled"}
#         else:
#             result = result[user["login"]]
#         if result["success"]:
#             await db.users.update_one({"_id": user["_id"]}, {"$set": {"bot_enabled": True}})
#         else:
#             pass
#     return JSONResponse(result, headers=response.headers)


# @api.post("/bot/disable")
# @logged_in
# async def disable_bot(request: Request, response: Response, user=None):
#     result = {"success": False, "error": "botnotinchannel"}
#     if user["bot_enabled"]:
#         await client.send_event(
#             to="twitchbot", event="channel_disconnected", data={"ids": [user["_id"]]}
#         )
#         await db.users.update_one({"_id": user["_id"]}, {"$set": {"bot_enabled": False}})
#         result = {"success": True, "error": ""}
#     return JSONResponse(result, headers=response.headers)
