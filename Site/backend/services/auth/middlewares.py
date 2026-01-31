from typing import Callable

from fastapi import Request, Response
from fastapi.routing import APIRoute
from fastapi.responses import RedirectResponse

from holybot_shared.db_models.factory import async_session_factory
from .cookie import set_session_cookie
from .session import get_session


class LoggedIn(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            async with async_session_factory() as db:
                redirect_response = RedirectResponse("/")
                session = request.cookies.get("session")
                if not session:
                    return redirect_response
                async with db.begin():
                    is_updated, session_obj = await get_session(session, db)
                if is_updated and session_obj is None:
                    redirect_response.delete_cookie("session")
                    return redirect_response
                response: Response = await original_route_handler(request)
                if is_updated:
                    set_session_cookie(response, session_obj)
                return response

        return custom_route_handler


class AdminOnly(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            async with async_session_factory() as db:
                redirect_response = RedirectResponse("/")
                session = request.cookies.get("session")
                if not session:
                    return redirect_response
                async with db.begin():
                    is_updated, session_obj = await get_session(session, db)
                if is_updated and session_obj is None:
                    redirect_response.delete_cookie("session")
                    return redirect_response
                if not session_obj.user.is_admin:
                    redirect_response.status_code = 403
                    return redirect_response
                response: Response = await original_route_handler(request)
                if is_updated:
                    set_session_cookie(response, session_obj)
                return response

        return custom_route_handler
