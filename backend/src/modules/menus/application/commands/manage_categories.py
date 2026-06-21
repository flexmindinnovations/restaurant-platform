import uuid
from dataclasses import dataclass

from modules.menus.application.ports.category_repository import CategoryRepository
from modules.menus.application.ports.menu_repository import MenuRepository
from modules.menus.domain.entities.category import Category
from shared.application.ports.unit_of_work import AbstractUnitOfWork
from shared.domain.exceptions import BusinessRuleViolationError, NotFoundException


@dataclass(frozen=True)
class AddCategoryCommand:
    menu_id: uuid.UUID
    name: str
    description: str | None = None
    display_order: int = 0


class AddCategoryHandler:
    def __init__(
        self,
        menu_repo: MenuRepository,
        category_repo: CategoryRepository,
        uow: AbstractUnitOfWork,
    ) -> None:
        self._menu_repo = menu_repo
        self._category_repo = category_repo
        self._uow = uow

    async def handle(self, command: AddCategoryCommand) -> uuid.UUID:
        async with self._uow:
            menu = await self._menu_repo.get_by_id(command.menu_id)
            if not menu:
                raise NotFoundException("Menu not found")

            if await self._category_repo.exists_by_name(command.menu_id, command.name):
                raise BusinessRuleViolationError(f'A category named "{command.name}" already exists in this menu')

            category = Category.create(
                menu_id=command.menu_id,
                name=command.name,
                description=command.description,
                display_order=command.display_order,
            )
            await self._category_repo.add(category)
            await self._uow.commit()

        return category.id


@dataclass(frozen=True)
class UpdateCategoryCommand:
    category_id: uuid.UUID
    name: str | None = None
    description: str | None = None
    display_order: int | None = None


class UpdateCategoryHandler:
    def __init__(self, category_repo: CategoryRepository, uow: AbstractUnitOfWork) -> None:
        self._category_repo = category_repo
        self._uow = uow

    async def handle(self, command: UpdateCategoryCommand) -> None:
        async with self._uow:
            category = await self._category_repo.get_by_id(command.category_id)
            if not category:
                raise NotFoundException("Category not found")

            category.update(
                name=command.name,
                description=command.description,
                display_order=command.display_order,
            )
            await self._category_repo.update(category)
            await self._uow.commit()


@dataclass(frozen=True)
class DeleteCategoryCommand:
    category_id: uuid.UUID


class DeleteCategoryHandler:
    def __init__(self, category_repo: CategoryRepository, uow: AbstractUnitOfWork) -> None:
        self._category_repo = category_repo
        self._uow = uow

    async def handle(self, command: DeleteCategoryCommand) -> None:
        async with self._uow:
            category = await self._category_repo.get_by_id(command.category_id)
            if not category:
                raise NotFoundException("Category not found")

            await self._category_repo.delete(command.category_id)
            await self._uow.commit()
