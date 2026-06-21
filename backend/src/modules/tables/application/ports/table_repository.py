import uuid
from abc import ABC, abstractmethod

from modules.tables.domain.entities.table import Table


class TableRepository(ABC):
    @abstractmethod
    async def add(self, table: Table) -> None: ...

    @abstractmethod
    async def get_by_id(self, table_id: uuid.UUID) -> Table | None: ...

    @abstractmethod
    async def update(self, table: Table) -> None: ...

    @abstractmethod
    async def delete(self, table_id: uuid.UUID) -> None: ...

    @abstractmethod
    async def list_by_restaurant(
        self,
        restaurant_id: uuid.UUID,
        section_id: uuid.UUID | None = None,
        active_only: bool = False,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Table]: ...

    @abstractmethod
    async def count_by_restaurant(
        self,
        restaurant_id: uuid.UUID,
        active_only: bool = False,
    ) -> int: ...

    @abstractmethod
    async def exists_by_number(self, restaurant_id: uuid.UUID, number: str) -> bool: ...
