from sqlalchemy.ext.asyncio import AsyncSession

from shared.domain.entity import AggregateRoot
from shared.domain.events import EventBus


class UnitOfWork:
    def __init__(self, session: AsyncSession, event_bus: EventBus) -> None:
        self._session = session
        self._event_bus = event_bus
        self._aggregates: list[AggregateRoot] = []

    def register_aggregate(self, aggregate: AggregateRoot) -> None:
        self._aggregates.append(aggregate)

    async def commit(self) -> None:
        await self._session.commit()
        for aggregate in self._aggregates:
            events = aggregate.collect_events()
            await self._event_bus.publish_many(events)
        self._aggregates.clear()

    async def rollback(self) -> None:
        await self._session.rollback()
        self._aggregates.clear()

    async def __aenter__(self) -> "UnitOfWork":
        return self

    async def __aexit__(self, exc_type: type | None, exc_val: Exception | None, exc_tb: object) -> None:
        if exc_type is not None:
            await self.rollback()
