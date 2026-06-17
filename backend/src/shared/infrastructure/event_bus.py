from collections.abc import Callable, Coroutine
from typing import Any

import structlog

from shared.domain.events import DomainEvent, EventBus

logger = structlog.get_logger()

EventHandler = Callable[[Any], Coroutine[Any, Any, None]]


class InMemoryEventBus(EventBus):
    """In-memory event bus for local development. Replace with SNS/SQS in production."""

    def __init__(self) -> None:
        self._handlers: dict[type[DomainEvent], list[EventHandler]] = {}
        self._handlers_by_name: dict[str, list[EventHandler]] = {}

    def subscribe(self, event_type: type[DomainEvent], handler: EventHandler) -> None:
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def subscribe_by_name(self, event_name: str, handler: EventHandler) -> None:
        if event_name not in self._handlers_by_name:
            self._handlers_by_name[event_name] = []
        self._handlers_by_name[event_name].append(handler)

    async def publish(self, event: DomainEvent) -> None:
        event_type = type(event)
        handlers = [*self._handlers.get(event_type, []), *self._handlers_by_name.get(event_type.__name__, [])]
        logger.info("publishing_domain_event", event_type=event_type.__name__, handler_count=len(handlers))
        for handler in handlers:
            await handler(event)


_event_bus = InMemoryEventBus()


def get_event_bus() -> InMemoryEventBus:
    return _event_bus
