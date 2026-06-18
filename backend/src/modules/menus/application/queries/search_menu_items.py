import uuid
from dataclasses import dataclass

from modules.menus.application.ports.menu_item_repository import MenuItemRepository
from modules.menus.application.queries.get_menu_item import MenuItemDTO


@dataclass(frozen=True)
class SearchMenuItemsQuery:
    restaurant_id: uuid.UUID
    query: str
    available_only: bool = True
    skip: int = 0
    limit: int = 20


@dataclass(frozen=True)
class SearchMenuItemsResult:
    items: list[MenuItemDTO]
    total: int


class SearchMenuItemsHandler:
    def __init__(self, item_repo: MenuItemRepository) -> None:
        self._item_repo = item_repo

    async def handle(self, query: SearchMenuItemsQuery) -> SearchMenuItemsResult:
        items = await self._item_repo.search(
            restaurant_id=query.restaurant_id,
            query=query.query,
            available_only=query.available_only,
            skip=query.skip,
            limit=query.limit,
        )
        total = await self._item_repo.search_count(
            restaurant_id=query.restaurant_id,
            query=query.query,
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

        return SearchMenuItemsResult(items=dtos, total=total)
