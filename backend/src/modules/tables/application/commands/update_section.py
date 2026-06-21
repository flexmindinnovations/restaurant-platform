from __future__ import annotations

import uuid
from dataclasses import dataclass

from modules.tables.application.ports.section_repository import SectionRepository
from modules.tables.domain.exceptions import SectionNotFoundError
from shared.application.ports.unit_of_work import AbstractUnitOfWork


@dataclass(frozen=True)
class UpdateSectionCommand:
    section_id: uuid.UUID
    name: str | None = None
    description: str | None = None
    display_order: int | None = None


class UpdateSectionHandler:
    def __init__(self, section_repo: SectionRepository, uow: AbstractUnitOfWork) -> None:
        self._section_repo = section_repo
        self._uow = uow

    async def handle(self, command: UpdateSectionCommand) -> None:
        async with self._uow:
            section = await self._section_repo.get_by_id(command.section_id)
            if not section:
                raise SectionNotFoundError(str(command.section_id))

            section.update_details(
                name=command.name,
                description=command.description,
                display_order=command.display_order,
            )
            await self._section_repo.update(section)
            self._uow.register_aggregate(section)
            await self._uow.commit()
