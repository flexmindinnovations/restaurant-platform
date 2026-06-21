from __future__ import annotations

import uuid
from dataclasses import dataclass

from modules.tables.application.ports.section_repository import SectionRepository
from modules.tables.domain.exceptions import SectionNotFoundError
from shared.application.ports.unit_of_work import AbstractUnitOfWork


@dataclass(frozen=True)
class DeleteSectionCommand:
    section_id: uuid.UUID


class DeleteSectionHandler:
    def __init__(self, section_repo: SectionRepository, uow: AbstractUnitOfWork) -> None:
        self._section_repo = section_repo
        self._uow = uow

    async def handle(self, command: DeleteSectionCommand) -> None:
        async with self._uow:
            section = await self._section_repo.get_by_id(command.section_id)
            if not section:
                raise SectionNotFoundError(str(command.section_id))

            await self._section_repo.delete(command.section_id)
            await self._uow.commit()
