import uuid
from dataclasses import dataclass

from modules.menus.application.ports.menu_repository import MenuRepository
from shared.application.ports.unit_of_work import AbstractUnitOfWork
from shared.domain.exceptions import NotFoundException


@dataclass(frozen=True)
class DeleteMenuCommand:
    menu_id: uuid.UUID


class DeleteMenuHandler:
    def __init__(self, menu_repo: MenuRepository, uow: AbstractUnitOfWork) -> None:
        self._menu_repo = menu_repo
        self._uow = uow

    async def handle(self, command: DeleteMenuCommand) -> None:
        async with self._uow:
            menu = await self._menu_repo.get_by_id(command.menu_id)
            if not menu:
                raise NotFoundException("Menu not found")

            await self._menu_repo.delete(command.menu_id)
            await self._uow.commit()
