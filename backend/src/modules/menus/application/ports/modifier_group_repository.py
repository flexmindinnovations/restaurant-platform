import uuid
from abc import ABC, abstractmethod

from modules.menus.domain.entities.modifier import ModifierGroup


class ModifierGroupRepository(ABC):
    @abstractmethod
    async def add(self, group: ModifierGroup) -> None: ...

    @abstractmethod
    async def get_by_id(self, group_id: uuid.UUID) -> ModifierGroup | None: ...

    @abstractmethod
    async def update(self, group: ModifierGroup) -> None: ...

    @abstractmethod
    async def delete(self, group_id: uuid.UUID) -> None: ...

    @abstractmethod
    async def list_by_menu_item(self, menu_item_id: uuid.UUID) -> list[ModifierGroup]: ...
