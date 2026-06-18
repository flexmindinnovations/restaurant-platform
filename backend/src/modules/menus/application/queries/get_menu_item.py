import uuid
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from modules.menus.application.ports.menu_item_repository import MenuItemRepository
from shared.domain.exceptions import NotFoundException


@dataclass(frozen=True)
class MenuItemDTO:
    id: uuid.UUID
    menu_id: uuid.UUID
    category_id: uuid.UUID | None
    restaurant_id: uuid.UUID
    name: str
    description: str | None
    price_amount: Decimal
    price_currency: str
    image_url: str | None
    display_order: int
    is_available: bool
    dietary_labels: list[str]
    preparation_time_minutes: int | None
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class GetMenuItemQuery:
    item_id: uuid.UUID


class GetMenuItemHandler:
    def __init__(self, item_repo: MenuItemRepository) -> None:
        self._item_repo = item_repo

    async def handle(self, query: GetMenuItemQuery) -> MenuItemDTO:
        item = await self._item_repo.get_by_id(query.item_id)
        if not item:
            raise NotFoundException("Menu item not found")

        return MenuItemDTO(
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
