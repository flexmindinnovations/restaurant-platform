import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.tables.application.ports.table_repository import TableRepository
from modules.tables.domain.entities.table import Table
from modules.tables.domain.value_objects.table_shape import TableShape
from modules.tables.domain.value_objects.table_status import TableStatus
from modules.tables.infrastructure.models.table_models import TableModel


class SqlAlchemyTableRepository(TableRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, table: Table) -> None:
        model = TableModel(
            id=table.id,
            restaurant_id=table.restaurant_id,
            section_id=table.section_id,
            number=table.number,
            capacity_min=table.capacity_min,
            capacity_max=table.capacity_max,
            shape=table.shape.value,
            position_x=table.position_x,
            position_y=table.position_y,
            status=table.status.value,
            turn_time_minutes=table.turn_time_minutes,
            buffer_minutes=table.buffer_minutes,
            is_active=table.is_active,
            created_at=table.created_at,
            updated_at=table.updated_at,
        )
        self._session.add(model)

    async def get_by_id(self, table_id: uuid.UUID) -> Table | None:
        result = await self._session.execute(select(TableModel).where(TableModel.id == table_id))
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_domain(model)

    async def update(self, table: Table) -> None:
        result = await self._session.execute(select(TableModel).where(TableModel.id == table.id))
        model = result.scalar_one_or_none()
        if model:
            model.section_id = table.section_id
            model.number = table.number
            model.capacity_min = table.capacity_min
            model.capacity_max = table.capacity_max
            model.shape = table.shape.value
            model.position_x = table.position_x
            model.position_y = table.position_y
            model.status = table.status.value
            model.turn_time_minutes = table.turn_time_minutes
            model.buffer_minutes = table.buffer_minutes
            model.is_active = table.is_active
            model.updated_at = table.updated_at

    async def delete(self, table_id: uuid.UUID) -> None:
        result = await self._session.execute(select(TableModel).where(TableModel.id == table_id))
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)

    async def list_by_restaurant(
        self,
        restaurant_id: uuid.UUID,
        section_id: uuid.UUID | None = None,
        active_only: bool = False,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Table]:
        query = select(TableModel).where(TableModel.restaurant_id == restaurant_id)
        if section_id is not None:
            query = query.where(TableModel.section_id == section_id)
        if active_only:
            query = query.where(TableModel.is_active.is_(True))
        query = query.order_by(TableModel.number).offset(skip).limit(limit)
        result = await self._session.execute(query)
        return [self._to_domain(m) for m in result.scalars().all()]

    async def count_by_restaurant(
        self,
        restaurant_id: uuid.UUID,
        active_only: bool = False,
    ) -> int:
        query = select(func.count(TableModel.id)).where(TableModel.restaurant_id == restaurant_id)
        if active_only:
            query = query.where(TableModel.is_active.is_(True))
        result = await self._session.execute(query)
        return result.scalar_one()

    async def exists_by_number(self, restaurant_id: uuid.UUID, number: str) -> bool:
        query = select(func.count(TableModel.id)).where(
            TableModel.restaurant_id == restaurant_id,
            TableModel.number == number,
        )
        result = await self._session.execute(query)
        return result.scalar_one() > 0

    def _to_domain(self, model: TableModel) -> Table:
        return Table(
            id=model.id,
            restaurant_id=model.restaurant_id,
            section_id=model.section_id,
            number=model.number,
            capacity_min=model.capacity_min,
            capacity_max=model.capacity_max,
            shape=TableShape(model.shape),
            position_x=model.position_x,
            position_y=model.position_y,
            status=TableStatus(model.status),
            turn_time_minutes=model.turn_time_minutes,
            buffer_minutes=model.buffer_minutes,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
