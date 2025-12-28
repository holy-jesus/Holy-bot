from typing import Callable

from fastapi import Request, Response
from fastapi.routing import APIRoute
from fastapi.responses import RedirectResponse

from .token import verify_session, set_token_cookie


class LoggedIn(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            redirect_response = RedirectResponse("/")
            token = request.cookies.get("token")
            if not token:
                return redirect_response
            new_token = await verify_session(token)
            if new_token is None:
                redirect_response.delete_cookie("token")
                return redirect_response
            response: Response = await original_route_handler(request)
            if isinstance(new_token, str):
                set_token_cookie(response, new_token)
            return response

        return custom_route_handler
