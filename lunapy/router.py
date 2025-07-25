import inspect
from typing import Callable, Awaitable
from lunapy.type import LunaEventName


class Router:
    def __init__(self):
        self._handlers: list[tuple[LunaEventName, Callable[..., Awaitable[None]]]] = []

    def on_event(self, name: LunaEventName):
        def decorator(func: Callable[..., Awaitable[None]]):
            if not inspect.iscoroutinefunction(func):
                raise Exception(f"{func}는 코루틴 함수가 아닙니다")

            self._handlers.append((name, func))
            return func

        return decorator

    def get_handlers(self):
        return self._handlers
