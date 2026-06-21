from __future__ import annotations

import uuid
from dataclasses import dataclass

from modules.tables.application.ports.table_repository import TableRepository
from modules.tables.domain.exceptions import TableNotFoundError
from modules.tables.domain.value_objects.table_status import TableStatus
from shared.application.ports.unit_of_work import AbstractUnitOfWork


@dataclass(frozen=True)
class UpdateTableStatusCommand:
    table_id: uuid.UUID
    status: TableStatus
    changed_by: uuid.UUID | None = None


class UpdateTableStatusHandler:
    def __init__(self, table_repo: TableRepository, uow: AbstractUnitOfWork) -> None:
        self._table_repo = table_repo
        self._uow = uow

    async def handle(self, command: UpdateTableStatusCommand) -> None:
        async with self._uow:
            table = await self._table_repo.get_by_id(command.table_id)
            if not table:
                raise TableNotFoundError(str(command.table_id))

            table.change_status(command.status, changed_by=command.changed_by)
            await self._table_repo.update(table)
            self._uow.register_aggregate(table)
            await self._uow.commit()
