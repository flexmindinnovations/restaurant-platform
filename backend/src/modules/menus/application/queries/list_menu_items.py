import uuid
from dataclasses import dataclass

from modules.menus.application.ports.menu_item_repository import MenuItemRepository
from modules.menus.application.queries.get_menu_item import MenuItemDTO


@dataclass(frozen=True)
class ListMenuItemsQuery:
    menu_id: uuid.UUID
    category_id: uuid.UUID | None = None
    available_only: bool = False
    skip: int = 0
    limit: int = 50


@dataclass(frozen=True)
class ListMenuItemsResult:
    items: list[MenuItemDTO]
    total: int


class ListMenuItemsHandler:
    def __init__(self, item_repo: MenuItemRepository) -> None:
        self._item_repo = item_repo

    async def handle(self, query: ListMenuItemsQuery) -> ListMenuItemsResult:
        items = await self._item_repo.list_by_menu(
            menu_id=query.menu_id,
            category_id=query.category_id,
            available_only=query.available_only,
            skip=query.skip,
            limit=query.limit,
        )
        total = await self._item_repo.count_by_menu(
            menu_id=query.menu_id,
            category_id=query.category_id,
            available_only=query.available_only,
        )

        dtos = [
            MenuItemDTO(
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
            for item in items
        ]

        return ListMenuItemsResult(items=dtos, total=total)
