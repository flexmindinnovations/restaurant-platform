import uuid
from abc import ABC, abstractmethod

from modules.menus.domain.entities.menu_item import MenuItem


class MenuItemRepository(ABC):
    @abstractmethod
    async def add(self, item: MenuItem) -> None: ...

    @abstractmethod
    async def get_by_id(self, item_id: uuid.UUID) -> MenuItem | None: ...

    @abstractmethod
    async def update(self, item: MenuItem) -> None: ...

    @abstractmethod
    async def delete(self, item_id: uuid.UUID) -> None: ...

    @abstractmethod
    async def list_by_menu(
        self,
        menu_id: uuid.UUID,
        category_id: uuid.UUID | None = None,
        available_only: bool = False,
        skip: int = 0,
        limit: int = 50,
    ) -> list[MenuItem]: ...

    @abstractmethod
    async def count_by_menu(
        self,
        menu_id: uuid.UUID,
        category_id: uuid.UUID | None = None,
        available_only: bool = False,
    ) -> int: ...
