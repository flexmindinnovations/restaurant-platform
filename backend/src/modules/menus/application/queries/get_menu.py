import uuid
from dataclasses import dataclass
from datetime import datetime

from modules.menus.application.ports.category_repository import CategoryRepository
from modules.menus.application.ports.menu_repository import MenuRepository
from shared.domain.exceptions import NotFoundException


@dataclass(frozen=True)
class CategoryDTO:
    id: uuid.UUID
    menu_id: uuid.UUID
    name: str
    description: str | None
    display_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class MenuDTO:
    id: uuid.UUID
    restaurant_id: uuid.UUID
    name: str
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    categories: list[CategoryDTO]


@dataclass(frozen=True)
class GetMenuQuery:
    menu_id: uuid.UUID


class GetMenuHandler:
    def __init__(self, menu_repo: MenuRepository, category_repo: CategoryRepository) -> None:
        self._menu_repo = menu_repo
        self._category_repo = category_repo

    async def handle(self, query: GetMenuQuery) -> MenuDTO:
        menu = await self._menu_repo.get_by_id(query.menu_id)
        if not menu:
            raise NotFoundException("Menu not found")

        categories = await self._category_repo.list_by_menu(menu.id)
        category_dtos = [
            CategoryDTO(
                id=c.id,
                menu_id=c.menu_id,
                name=c.name,
                description=c.description,
                display_order=c.display_order,
                is_active=c.is_active,
                created_at=c.created_at,
                updated_at=c.updated_at,
            )
            for c in sorted(categories, key=lambda c: c.display_order)
        ]

        return MenuDTO(
            id=menu.id,
            restaurant_id=menu.restaurant_id,
            name=menu.name,
            description=menu.description,
            is_active=menu.is_active,
            created_at=menu.created_at,
            updated_at=menu.updated_at,
            categories=category_dtos,
        )
