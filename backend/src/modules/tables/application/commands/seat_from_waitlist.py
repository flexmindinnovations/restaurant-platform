from __future__ import annotations

import uuid
from dataclasses import dataclass

from modules.tables.application.ports.table_repository import TableRepository
from modules.tables.application.ports.waitlist_repository import WaitlistRepository
from modules.tables.domain.exceptions import TableNotFoundError, WaitlistEntryNotFoundError
from modules.tables.domain.value_objects.table_status import TableStatus
from shared.application.ports.unit_of_work import AbstractUnitOfWork


@dataclass(frozen=True)
class SeatFromWaitlistCommand:
    entry_id: uuid.UUID
    table_id: uuid.UUID


class SeatFromWaitlistHandler:
    def __init__(
        self,
        waitlist_repo: WaitlistRepository,
        table_repo: TableRepository,
        uow: AbstractUnitOfWork,
    ) -> None:
        self._waitlist_repo = waitlist_repo
        self._table_repo = table_repo
        self._uow = uow

    async def handle(self, command: SeatFromWaitlistCommand) -> None:
        async with self._uow:
            entry = await self._waitlist_repo.get_by_id(command.entry_id)
            if not entry:
                raise WaitlistEntryNotFoundError(str(command.entry_id))

            table = await self._table_repo.get_by_id(command.table_id)
            if not table:
                raise TableNotFoundError(str(command.table_id))

            entry.seat()
            table.change_status(TableStatus.OCCUPIED)

            await self._waitlist_repo.update(entry)
            await self._table_repo.update(table)
            self._uow.register_aggregate(entry)
            self._uow.register_aggregate(table)
            await self._uow.commit()
