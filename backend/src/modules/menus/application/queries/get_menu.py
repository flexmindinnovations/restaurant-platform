import uuid
from dataclasses import dataclass, field
from datetime import datetime

from modules.menus.application.ports.category_repository import CategoryRepository
from modules.menus.application.ports.menu_item_repository import MenuItemRepository
from modules.menus.application.ports.menu_repository import MenuRepository
from modules.menus.application.queries.get_menu_item import MenuItemDTO
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
    items: list[MenuItemDTO] = field(default_factory=list)


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
    def __init__(
        self,
        menu_repo: MenuRepository,
        category_repo: CategoryRepository,
        item_repo: MenuItemRepository,
    ) -> None:
        self._menu_repo = menu_repo
        self._category_repo = category_repo
        self._item_repo = item_repo

    async def handle(self, query: GetMenuQuery) -> MenuDTO:
        menu = await self._menu_repo.get_by_id(query.menu_id)
        if not menu:
            raise NotFoundException("Menu not found")

        categories = await self._category_repo.list_by_menu(menu.id)
        items = await self._item_repo.list_by_menu(menu.id)

        items_by_category: dict[uuid.UUID | None, list[MenuItemDTO]] = {}
        for item in items:
            item_dto = MenuItemDTO(
                id=item.id,
                menu_id=item.menu_id,
                category_id=item.category_id,
                restaurant_id=item.restaurant_id,
                name=item.name,
                description=item.description,
                price_amount=item.price.amount,
                price_currency=item.price.currency,
                image_url=item.image_url,
                display_order=item.display_order,
                is_available=item.is_available,
                dietary_labels=item.dietary_labels,
                preparation_time_minutes=item.preparation_time_minutes,
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
            items_by_category.setdefault(item.category_id, []).append(item_dto)

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
                items=sorted(items_by_category.get(c.id, []), key=lambda i: i.display_order),
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
