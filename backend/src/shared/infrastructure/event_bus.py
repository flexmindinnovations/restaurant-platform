import structlog

from shared.domain.entity import DomainEvent
from shared.domain.events import EventBus

logger = structlog.get_logger()


class InMemoryEventBus(EventBus):
    """In-memory event bus for local development. Replace with SNS/SQS in production."""

    def __init__(self) -> None:
        self._handlers: dict[type[DomainEvent], list] = {}

    def subscribe(self, event_type: type[DomainEvent], handler: object) -> None:
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    async def publish(self, event: DomainEvent) -> None:
        event_type = type(event)
        handlers = self._handlers.get(event_type, [])
        logger.info("publishing_domain_event", event_type=event_type.__name__, handler_count=len(handlers))
        for handler in handlers:
            await handler(event)
