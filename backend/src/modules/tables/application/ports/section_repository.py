import uuid
from abc import ABC, abstractmethod

from modules.tables.domain.entities.section import Section


class SectionRepository(ABC):
    @abstractmethod
    async def add(self, section: Section) -> None: ...

    @abstractmethod
    async def get_by_id(self, section_id: uuid.UUID) -> Section | None: ...

    @abstractmethod
    async def update(self, section: Section) -> None: ...

    @abstractmethod
    async def delete(self, section_id: uuid.UUID) -> None: ...

    @abstractmethod
    async def list_by_restaurant(
        self,
        restaurant_id: uuid.UUID,
        active_only: bool = False,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Section]: ...
