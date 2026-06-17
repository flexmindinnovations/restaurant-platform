from sqlalchemy.ext.asyncio import AsyncSession

from shared.application.ports.unit_of_work import AbstractUnitOfWork
from shared.domain.events import EventBus
from shared.infrastructure.outbox import store_outbox_events


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session: AsyncSession, event_bus: EventBus) -> None:
        super().__init__()
        self._session = session
        self._event_bus = event_bus

    async def commit(self) -> None:
        collected_events = []
        for aggregate in self._aggregates:
            collected_events.extend(aggregate.collect_events())
        # Persist events to outbox within the same transaction
        await store_outbox_events(self._session, collected_events)
        await self._session.commit()
        # Publish after commit for immediate in-process handling
        await self._event_bus.publish_many(collected_events)
        self._aggregates.clear()

    async def rollback(self) -> None:
        await self._session.rollback()
        self._aggregates.clear()


UnitOfWork = SqlAlchemyUnitOfWork
