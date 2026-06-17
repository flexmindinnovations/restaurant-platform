from typing import Protocol

from shared.domain.events import EventBus


class EventSubscriber(Protocol):
    def subscribe(self, event_bus: EventBus) -> None: ...
