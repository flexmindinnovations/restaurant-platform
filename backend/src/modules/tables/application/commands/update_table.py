from __future__ import annotations

import uuid
from dataclasses import dataclass

from modules.tables.application.ports.table_repository import TableRepository
from modules.tables.domain.exceptions import TableNotFoundError
from modules.tables.domain.value_objects.table_shape import TableShape
from shared.application.ports.unit_of_work import AbstractUnitOfWork


@dataclass(frozen=True)
class UpdateTableCommand:
    table_id: uuid.UUID
    number: str | None = None
    capacity_min: int | None = None
    capacity_max: int | None = None
    shape: TableShape | None = None
    section_id: uuid.UUID | None = None
    position_x: int | None = None
    position_y: int | None = None
    turn_time_minutes: int | None = None
    buffer_minutes: int | None = None


class UpdateTableHandler:
    def __init__(self, table_repo: TableRepository, uow: AbstractUnitOfWork) -> None:
        self._table_repo = table_repo
        self._uow = uow

    async def handle(self, command: UpdateTableCommand) -> None:
        async with self._uow:
            table = await self._table_repo.get_by_id(command.table_id)
            if not table:
                raise TableNotFoundError(str(command.table_id))

            table.update_details(
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
            await self._table_repo.update(table)
            self._uow.register_aggregate(table)
            await self._uow.commit()
