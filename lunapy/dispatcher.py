import asyncio
import traceback
import inspect
from typing import Callable, Awaitable, List, Type, Dict, Any, get_type_hints
from dataclasses import dataclass

from lunapy.type import LunaEventName


@dataclass
class HandlerInfo:
    handler: Callable[..., Awaitable[None]]
    param_types: List[Type[Any]]
    file_path: str
    module_name: str
    func_name: str


class Dispatcher:
    def __init__(self):
        self._handlers: Dict[str, List[HandlerInfo]] = {}

    def register(
        self, event_name: LunaEventName, handler: Callable[..., Awaitable[None]]
    ) -> None:
        sig = inspect.signature(handler)
        type_hints = get_type_hints(handler)

        param_types = []
        for param in sig.parameters.values():
            if param.name not in type_hints:
                raise TypeError(
                    f"{handler.__name__}의 파라메터 {param.name}에 타입 힌트가 없습니다"
                )
            param_types.append(type_hints[param.name])

        file_path = inspect.getfile(handler)
        module_name = handler.__module__
        func_name = handler.__name__

        info = HandlerInfo(
            handler=handler,
            param_types=param_types,
            file_path=file_path,
            module_name=module_name,
            func_name=func_name,
        )

        self._handlers.setdefault(event_name, []).append(info)

    def dispatch(
        self, event_name: LunaEventName, container: Dict[Type[Any], Any]
    ) -> None:
        for info in self._handlers.get(event_name, []):
            try:
                args = [container[typ] for typ in info.param_types]
            except KeyError as e:
                print(
                    f"{info.func_name}의 인자 중 {e.args[0].__name__} 타입이 제공되지 않았습니다 ({info.file_path} {info.module_name})"
                )
                continue

            async def run_handler():
                try:
                    await info.handler(*args)
                except Exception:
                    traceback.print_exc()

            asyncio.create_task(run_handler())
