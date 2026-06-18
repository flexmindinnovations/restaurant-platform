import uuid
from abc import ABC, abstractmethod

from modules.menus.domain.entities.menu import Menu


class MenuRepository(ABC):
    @abstractmethod
    async def add(self, menu: Menu) -> None: ...

    @abstractmethod
    async def get_by_id(self, menu_id: uuid.UUID) -> Menu | None: ...

    @abstractmethod
    async def update(self, menu: Menu) -> None: ...

    @abstractmethod
    async def delete(self, menu_id: uuid.UUID) -> None: ...

    @abstractmethod
    async def list_by_restaurant(
        self,
        restaurant_id: uuid.UUID,
        skip: int = 0,
        limit: int = 20,
        active_only: bool = False,
    ) -> list[Menu]: ...

    @abstractmethod
    async def count_by_restaurant(
        self,
        restaurant_id: uuid.UUID,
        active_only: bool = False,
    ) -> int: ...
