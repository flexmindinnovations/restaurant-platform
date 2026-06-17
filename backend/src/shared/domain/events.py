import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True)
class DomainEvent:
    aggregate_id: uuid.UUID
    event_id: uuid.UUID = field(default_factory=uuid.uuid4)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))


class EventBus:
    """Interface for the domain event bus. Implementation in infrastructure layer."""

    async def publish(self, event: DomainEvent) -> None:
        raise NotImplementedError

    async def publish_many(self, events: list[DomainEvent]) -> None:
        for event in events:
            await self.publish(event)
