from __future__ import annotations

import uuid
from dataclasses import dataclass

from modules.tables.application.ports.table_repository import TableRepository
from modules.tables.domain.exceptions import TableNotFoundError
from shared.application.ports.unit_of_work import AbstractUnitOfWork


@dataclass(frozen=True)
class DeleteTableCommand:
    table_id: uuid.UUID


class DeleteTableHandler:
    def __init__(self, table_repo: TableRepository, uow: AbstractUnitOfWork) -> None:
        self._table_repo = table_repo
        self._uow = uow

    async def handle(self, command: DeleteTableCommand) -> None:
        async with self._uow:
            table = await self._table_repo.get_by_id(command.table_id)
            if not table:
                raise TableNotFoundError(str(command.table_id))

            await self._table_repo.delete(command.table_id)
            await self._uow.commit()
