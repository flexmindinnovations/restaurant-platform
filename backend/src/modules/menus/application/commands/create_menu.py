import uuid
from dataclasses import dataclass

from modules.menus.application.ports.menu_repository import MenuRepository
from modules.menus.domain.entities.menu import Menu
from shared.application.ports.unit_of_work import AbstractUnitOfWork


@dataclass(frozen=True)
class CreateMenuCommand:
    restaurant_id: uuid.UUID
    name: str
    description: str | None = None


class CreateMenuHandler:
    def __init__(self, menu_repo: MenuRepository, uow: AbstractUnitOfWork) -> None:
        self._menu_repo = menu_repo
        self._uow = uow

    async def handle(self, command: CreateMenuCommand) -> uuid.UUID:
        menu = Menu.create(
            restaurant_id=command.restaurant_id,
            name=command.name,
            description=command.description,
        )

        async with self._uow:
            await self._menu_repo.add(menu)
            self._uow.register_aggregate(menu)
            await self._uow.commit()

        return menu.id
