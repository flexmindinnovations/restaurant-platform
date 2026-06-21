from __future__ import annotations

import uuid
from dataclasses import dataclass

from modules.tables.application.ports.section_repository import SectionRepository
from modules.tables.domain.entities.section import Section
from shared.application.ports.unit_of_work import AbstractUnitOfWork


@dataclass(frozen=True)
class CreateSectionCommand:
    restaurant_id: uuid.UUID
    name: str
    description: str | None = None
    display_order: int = 0


class CreateSectionHandler:
    def __init__(self, section_repo: SectionRepository, uow: AbstractUnitOfWork) -> None:
        self._section_repo = section_repo
        self._uow = uow

    async def handle(self, command: CreateSectionCommand) -> uuid.UUID:
        async with self._uow:
            section = Section.create(
                restaurant_id=command.restaurant_id,
                name=command.name,
                description=command.description,
                display_order=command.display_order,
            )
            await self._section_repo.add(section)
            self._uow.register_aggregate(section)
            await self._uow.commit()

        return section.id
