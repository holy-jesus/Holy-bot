from holybot_shared.communicator import Client

from holybot_shared.SharedProto.holybot.api import UserLoggedIn


async def auth(client: Client, user_id: str, code: str, redirect_uri: str):
    response = await client.API.get_token(
        UserLoggedIn(user_id=user_id, code=code, redirect_uri=redirect_uri)
    )

    return ""
