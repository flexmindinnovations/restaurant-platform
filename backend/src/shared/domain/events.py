from shared.domain.entity import DomainEvent


class EventBus:
    """Interface for the domain event bus. Implementation in infrastructure layer."""

    async def publish(self, event: DomainEvent) -> None:
        raise NotImplementedError

    async def publish_many(self, events: list[DomainEvent]) -> None:
        for event in events:
            await self.publish(event)
