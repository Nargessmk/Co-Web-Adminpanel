from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Generic, TypeVar

logger = logging.getLogger(__name__)

TRequest = TypeVar("TRequest")
TResponse = TypeVar("TResponse")


@dataclass
class Request(Generic[TResponse]):
    pass


class IRequestHandler(Generic[TRequest, TResponse]):
    async def handle(self, request: TRequest) -> TResponse:
        raise NotImplementedError


@dataclass
class Notification:
    pass


class INotificationHandler(Generic[TRequest]):
    async def handle(self, notification: TRequest) -> None:
        raise NotImplementedError


class IPipelineBehavior(Generic[TRequest, TResponse]):
    async def handle(
        self,
        request: TRequest,
        next_handler: Callable[[TRequest], TResponse],
    ) -> TResponse:
        raise NotImplementedError


class Mediator:
    def __init__(self):
        self._request_handlers: dict[type, IRequestHandler] = {}
        self._notification_handlers: dict[type, list[INotificationHandler]] = {}
        self._behaviors: list[IPipelineBehavior] = []

    def register_request_handler(
        self, request_type: type, handler: IRequestHandler
    ) -> None:
        self._request_handlers[request_type] = handler

    def register_notification_handler(
        self, notification_type: type, handler: INotificationHandler
    ) -> None:
        self._notification_handlers.setdefault(notification_type, []).append(handler)

    def add_behavior(self, behavior: IPipelineBehavior) -> None:
        self._behaviors.append(behavior)

    async def send(self, request: Request) -> Any:
        handler = self._request_handlers.get(type(request))
        if handler is None:
            raise ValueError(f"No handler registered for {type(request).__name__}")

        async def next_handler(req: Request) -> Any:
            return await handler.handle(req)

        pipeline = next_handler
        for behavior in reversed(self._behaviors):
            prev = pipeline

            async def wrap(b: IPipelineBehavior, nxt: Callable) -> Callable:
                async def inner(req: Request) -> Any:
                    return await b.handle(req, nxt)
                return inner

            pipeline = await wrap(behavior, pipeline)

        return await pipeline(request)

    async def publish(self, notification: Notification) -> None:
        handlers = self._notification_handlers.get(type(notification), [])
        for handler in handlers:
            await handler.handle(notification)


_mediator: Mediator | None = None


def get_mediator() -> Mediator:
    global _mediator
    if _mediator is None:
        _mediator = Mediator()
    return _mediator