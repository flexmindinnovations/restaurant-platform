from abc import ABC, abstractmethod
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession

from shared.domain.entity import AggregateRoot
from shared.domain.events import EventBus


class AbstractUnitOfWork(ABC):
    def __init__(self) -> None:
        self._aggregates: list[AggregateRoot] = []

    def register_aggregate(self, aggregate: AggregateRoot) -> None:
        self._aggregates.append(aggregate)

    @abstractmethod
    async def commit(self) -> None:
        pass

    @abstractmethod
    async def rollback(self) -> None:
        pass

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type: type | None, exc_val: Exception | None, exc_tb: object) -> None:
        if exc_type is not None:
            await self.rollback()


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session: AsyncSession, event_bus: EventBus) -> None:
        super().__init__()
        self._session = session
        self._event_bus = event_bus

    async def commit(self) -> None:
        await self._session.commit()
        for aggregate in self._aggregates:
            events = aggregate.collect_events()
            await self._event_bus.publish_many(events)
        self._aggregates.clear()

    async def rollback(self) -> None:
        await self._session.rollback()
        self._aggregates.clear()


# Alias for backward compatibility / simplicity
UnitOfWork = SqlAlchemyUnitOfWork
