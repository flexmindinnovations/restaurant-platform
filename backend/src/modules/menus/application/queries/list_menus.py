import uuid
from dataclasses import dataclass

from modules.menus.application.ports.category_repository import CategoryRepository
from modules.menus.application.ports.menu_item_repository import MenuItemRepository
from modules.menus.application.ports.menu_repository import MenuRepository
from modules.menus.application.queries.get_menu import CategoryDTO, MenuDTO
from modules.menus.application.queries.get_menu_item import MenuItemDTO


@dataclass(frozen=True)
class ListMenusQuery:
    restaurant_id: uuid.UUID
    skip: int = 0
    limit: int = 20
    active_only: bool = False


@dataclass(frozen=True)
class ListMenusResult:
    items: list[MenuDTO]
    total: int


class ListMenusHandler:
    def __init__(
        self,
        menu_repo: MenuRepository,
        category_repo: CategoryRepository,
        item_repo: MenuItemRepository,
    ) -> None:
        self._menu_repo = menu_repo
        self._category_repo = category_repo
        self._item_repo = item_repo

    async def handle(self, query: ListMenusQuery) -> ListMenusResult:
        menus = await self._menu_repo.list_by_restaurant(
            restaurant_id=query.restaurant_id,
            skip=query.skip,
            limit=query.limit,
            active_only=query.active_only,
        )
        total = await self._menu_repo.count_by_restaurant(
            restaurant_id=query.restaurant_id,
            active_only=query.active_only,
        )

        dtos = []
        for m in menus:
            categories = await self._category_repo.list_by_menu(m.id)
            items = await self._item_repo.list_by_menu(m.id)

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
            dtos.append(
                MenuDTO(
                    id=m.id,
                    restaurant_id=m.restaurant_id,
                    name=m.name,
                    description=m.description,
                    is_active=m.is_active,
                    created_at=m.created_at,
                    updated_at=m.updated_at,
                    categories=category_dtos,
                )
            )

        return ListMenusResult(items=dtos, total=total)
