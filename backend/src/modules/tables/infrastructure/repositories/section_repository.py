import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.tables.application.ports.section_repository import SectionRepository
from modules.tables.domain.entities.section import Section
from modules.tables.infrastructure.models.table_models import SectionModel


class SqlAlchemySectionRepository(SectionRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, section: Section) -> None:
        model = SectionModel(
            id=section.id,
            restaurant_id=section.restaurant_id,
            name=section.name,
            description=section.description,
            display_order=section.display_order,
            is_active=section.is_active,
            created_at=section.created_at,
            updated_at=section.updated_at,
        )
        self._session.add(model)

    async def get_by_id(self, section_id: uuid.UUID) -> Section | None:
        result = await self._session.execute(select(SectionModel).where(SectionModel.id == section_id))
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_domain(model)

    async def update(self, section: Section) -> None:
        result = await self._session.execute(select(SectionModel).where(SectionModel.id == section.id))
        model = result.scalar_one_or_none()
        if model:
            model.name = section.name
            model.description = section.description
            model.display_order = section.display_order
            model.is_active = section.is_active
            model.updated_at = section.updated_at

    async def delete(self, section_id: uuid.UUID) -> None:
        result = await self._session.execute(select(SectionModel).where(SectionModel.id == section_id))
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)

    async def list_by_restaurant(
        self,
        restaurant_id: uuid.UUID,
        active_only: bool = False,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Section]:
        query = select(SectionModel).where(SectionModel.restaurant_id == restaurant_id)
        if active_only:
            query = query.where(SectionModel.is_active.is_(True))
        query = query.order_by(SectionModel.display_order).offset(skip).limit(limit)
        result = await self._session.execute(query)
        return [self._to_domain(m) for m in result.scalars().all()]

    def _to_domain(self, model: SectionModel) -> Section:
        return Section(
            id=model.id,
            restaurant_id=model.restaurant_id,
            name=model.name,
            description=model.description,
            display_order=model.display_order,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
