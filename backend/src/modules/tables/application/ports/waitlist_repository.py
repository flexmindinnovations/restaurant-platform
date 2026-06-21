import uuid
from abc import ABC, abstractmethod

from modules.tables.domain.entities.waitlist_entry import WaitlistEntry


class WaitlistRepository(ABC):
    @abstractmethod
    async def add(self, entry: WaitlistEntry) -> None: ...

    @abstractmethod
    async def get_by_id(self, entry_id: uuid.UUID) -> WaitlistEntry | None: ...

    @abstractmethod
    async def update(self, entry: WaitlistEntry) -> None: ...

    @abstractmethod
    async def list_active_by_restaurant(
        self,
        restaurant_id: uuid.UUID,
        skip: int = 0,
        limit: int = 50,
    ) -> list[WaitlistEntry]: ...

    @abstractmethod
    async def get_next_position(self, restaurant_id: uuid.UUID) -> int: ...

    @abstractmethod
    async def count_active_by_restaurant(self, restaurant_id: uuid.UUID) -> int: ...
