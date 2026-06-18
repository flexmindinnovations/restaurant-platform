import uuid
from dataclasses import dataclass

from modules.menus.application.ports.menu_repository import MenuRepository
from shared.application.ports.unit_of_work import AbstractUnitOfWork
from shared.domain.exceptions import NotFoundException


@dataclass(frozen=True)
class UpdateMenuCommand:
    menu_id: uuid.UUID
    name: str | None = None
    description: str | None = None
    is_active: bool | None = None


class UpdateMenuHandler:
    def __init__(self, menu_repo: MenuRepository, uow: AbstractUnitOfWork) -> None:
        self._menu_repo = menu_repo
        self._uow = uow

    async def handle(self, command: UpdateMenuCommand) -> None:
        async with self._uow:
            menu = await self._menu_repo.get_by_id(command.menu_id)
            if not menu:
                raise NotFoundException("Menu not found")

            menu.update_details(
                name=command.name,
                description=command.description,
            )

            if command.is_active is True:
                menu.publish()
            elif command.is_active is False:
                menu.unpublish()

            await self._menu_repo.update(menu)
            self._uow.register_aggregate(menu)
            await self._uow.commit()
