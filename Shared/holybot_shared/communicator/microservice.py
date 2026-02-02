from typing import TYPE_CHECKING
import inspect

from betterproto2 import Message

if TYPE_CHECKING:
    from holybot_shared.communicator import Client


class Microservice:
    def __init__(self, client: "Client"):
        self.__client = client

        for name, value in inspect.getmembers(self):
            if name.startswith("_") or not inspect.iscoroutinefunction(value):
                continue

            sig = inspect.signature(value)
            return_type = (
                sig.return_annotation
                if sig.return_annotation != inspect._empty
                else None
            )

            async def wrapper(
                *args, _name=name, _sig=sig, _return_type=return_type, **kwargs
            ):
                bound = _sig.bind(*args, **kwargs)
                bound.apply_defaults()

                payload = bound.arguments.get("payload")
                timeout = bound.arguments.get("timeout", 10)

                return await self.__send_request(
                    _name, bool(_return_type), _return_type, payload, timeout
                )

            setattr(self, name, wrapper)

    def __send_request(
        self,
        function_name: str,
        response: bool,
        response_type: type,
        payload: Message,
        timeout: int,
    ):
        return self.__client.send_event(
            self.__class__.__name__,
            function_name,
            wait_for_response=response,
            response_type=response_type,
            payload=payload,
            timeout=timeout,
        )
