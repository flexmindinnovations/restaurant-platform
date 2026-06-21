import uuid
from abc import ABC, abstractmethod

from modules.menus.domain.entities.category import Category


class CategoryRepository(ABC):
    @abstractmethod
    async def add(self, category: Category) -> None: ...

    @abstractmethod
    async def get_by_id(self, category_id: uuid.UUID) -> Category | None: ...

    @abstractmethod
    async def update(self, category: Category) -> None: ...

    @abstractmethod
    async def delete(self, category_id: uuid.UUID) -> None: ...

    @abstractmethod
    async def list_by_menu(self, menu_id: uuid.UUID) -> list[Category]: ...

    @abstractmethod
    async def exists_by_name(self, menu_id: uuid.UUID, name: str) -> bool: ...
