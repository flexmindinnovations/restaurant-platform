from __future__ import annotations

import uuid
from dataclasses import dataclass

from modules.tables.application.ports.waitlist_repository import WaitlistRepository
from modules.tables.domain.exceptions import WaitlistEntryNotFoundError
from shared.application.ports.unit_of_work import AbstractUnitOfWork


@dataclass(frozen=True)
class NotifyWaitlistCommand:
    entry_id: uuid.UUID


class NotifyWaitlistHandler:
    def __init__(self, waitlist_repo: WaitlistRepository, uow: AbstractUnitOfWork) -> None:
        self._waitlist_repo = waitlist_repo
        self._uow = uow

    async def handle(self, command: NotifyWaitlistCommand) -> None:
        async with self._uow:
            entry = await self._waitlist_repo.get_by_id(command.entry_id)
            if not entry:
                raise WaitlistEntryNotFoundError(str(command.entry_id))

            entry.notify()
            await self._waitlist_repo.update(entry)
            self._uow.register_aggregate(entry)
            await self._uow.commit()
