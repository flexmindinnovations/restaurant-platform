import uuid
from dataclasses import dataclass

from modules.menus.application.ports.menu_repository import MenuRepository
from modules.menus.domain.entities.menu import Menu
from shared.application.ports.unit_of_work import AbstractUnitOfWork
from shared.domain.exceptions import BusinessRuleViolationError


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
        async with self._uow:
            if await self._menu_repo.exists_by_name(command.restaurant_id, command.name):
                raise BusinessRuleViolationError(f'A menu named "{command.name}" already exists for this restaurant')

            menu = Menu.create(
                restaurant_id=command.restaurant_id,
                name=command.name,
                description=command.description,
            )
            await self._menu_repo.add(menu)
            self._uow.register_aggregate(menu)
            await self._uow.commit()

        return menu.id
