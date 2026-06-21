import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.tables.application.ports.waitlist_repository import WaitlistRepository
from modules.tables.domain.entities.waitlist_entry import WaitlistEntry
from modules.tables.domain.value_objects.waitlist_status import WaitlistStatus
from modules.tables.infrastructure.models.table_models import WaitlistEntryModel


class SqlAlchemyWaitlistRepository(WaitlistRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, entry: WaitlistEntry) -> None:
        model = WaitlistEntryModel(
            id=entry.id,
            restaurant_id=entry.restaurant_id,
            customer_name=entry.customer_name,
            customer_phone=entry.customer_phone,
            customer_id=entry.customer_id,
            party_size=entry.party_size,
            estimated_wait_minutes=entry.estimated_wait_minutes,
            queue_position=entry.queue_position,
            status=entry.status.value,
            preferred_section=entry.preferred_section,
            special_requests=entry.special_requests,
            notified_at=entry.notified_at,
            seated_at=entry.seated_at,
            created_at=entry.created_at,
            updated_at=entry.updated_at,
        )
        self._session.add(model)

    async def get_by_id(self, entry_id: uuid.UUID) -> WaitlistEntry | None:
        result = await self._session.execute(
            select(WaitlistEntryModel).where(WaitlistEntryModel.id == entry_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_domain(model)

    async def update(self, entry: WaitlistEntry) -> None:
        result = await self._session.execute(
            select(WaitlistEntryModel).where(WaitlistEntryModel.id == entry.id)
        )
        model = result.scalar_one_or_none()
        if model:
            model.customer_name = entry.customer_name
            model.customer_phone = entry.customer_phone
            model.party_size = entry.party_size
            model.estimated_wait_minutes = entry.estimated_wait_minutes
            model.queue_position = entry.queue_position
            model.status = entry.status.value
            model.preferred_section = entry.preferred_section
            model.special_requests = entry.special_requests
            model.notified_at = entry.notified_at
            model.seated_at = entry.seated_at
            model.updated_at = entry.updated_at

    async def list_active_by_restaurant(
        self,
        restaurant_id: uuid.UUID,
        skip: int = 0,
        limit: int = 50,
    ) -> list[WaitlistEntry]:
        query = (
            select(WaitlistEntryModel)
            .where(
                WaitlistEntryModel.restaurant_id == restaurant_id,
                WaitlistEntryModel.status.in_([WaitlistStatus.WAITING.value, WaitlistStatus.NOTIFIED.value]),
            )
            .order_by(WaitlistEntryModel.queue_position)
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(query)
        return [self._to_domain(m) for m in result.scalars().all()]

    async def get_next_position(self, restaurant_id: uuid.UUID) -> int:
        query = select(func.coalesce(func.max(WaitlistEntryModel.queue_position), 0)).where(
            WaitlistEntryModel.restaurant_id == restaurant_id,
            WaitlistEntryModel.status.in_([WaitlistStatus.WAITING.value, WaitlistStatus.NOTIFIED.value]),
        )
        result = await self._session.execute(query)
        return result.scalar_one() + 1

    async def count_active_by_restaurant(self, restaurant_id: uuid.UUID) -> int:
        query = select(func.count(WaitlistEntryModel.id)).where(
            WaitlistEntryModel.restaurant_id == restaurant_id,
            WaitlistEntryModel.status.in_([WaitlistStatus.WAITING.value, WaitlistStatus.NOTIFIED.value]),
        )
        result = await self._session.execute(query)
        return result.scalar_one()

    def _to_domain(self, model: WaitlistEntryModel) -> WaitlistEntry:
        return WaitlistEntry(
            id=model.id,
            restaurant_id=model.restaurant_id,
            customer_name=model.customer_name,
            customer_phone=model.customer_phone,
            customer_id=model.customer_id,
            party_size=model.party_size,
            estimated_wait_minutes=model.estimated_wait_minutes,
            queue_position=model.queue_position,
            status=WaitlistStatus(model.status),
            preferred_section=model.preferred_section,
            special_requests=model.special_requests,
            notified_at=model.notified_at,
            seated_at=model.seated_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
