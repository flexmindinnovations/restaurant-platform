from __future__ import annotations

import uuid
from dataclasses import dataclass

from modules.tables.application.ports.table_repository import TableRepository
from modules.tables.domain.entities.table import Table
from modules.tables.domain.exceptions import DuplicateTableNumberError
from modules.tables.domain.value_objects.table_shape import TableShape
from shared.application.ports.unit_of_work import AbstractUnitOfWork


@dataclass(frozen=True)
class CreateTableCommand:
    restaurant_id: uuid.UUID
    number: str
    capacity_min: int
    capacity_max: int
    shape: TableShape = TableShape.RECTANGULAR
    section_id: uuid.UUID | None = None
    position_x: int = 0
    position_y: int = 0
    turn_time_minutes: int = 90
    buffer_minutes: int = 15


class CreateTableHandler:
    def __init__(self, table_repo: TableRepository, uow: AbstractUnitOfWork) -> None:
        self._table_repo = table_repo
        self._uow = uow

    async def handle(self, command: CreateTableCommand) -> uuid.UUID:
        async with self._uow:
            if await self._table_repo.exists_by_number(command.restaurant_id, command.number):
                raise DuplicateTableNumberError(str(command.restaurant_id), command.number)

            table = Table.create(
                restaurant_id=command.restaurant_id,
                number=command.number,
                capacity_min=command.capacity_min,
                capacity_max=command.capacity_max,
                shape=command.shape,
                section_id=command.section_id,
                position_x=command.position_x,
                position_y=command.position_y,
                turn_time_minutes=command.turn_time_minutes,
                buffer_minutes=command.buffer_minutes,
            )
            await self._table_repo.add(table)
            self._uow.register_aggregate(table)
            await self._uow.commit()

        return table.id
