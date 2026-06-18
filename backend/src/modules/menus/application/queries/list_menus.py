import uuid
from dataclasses import dataclass

from modules.menus.application.ports.menu_repository import MenuRepository
from modules.menus.application.queries.get_menu import MenuDTO


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
    def __init__(self, menu_repo: MenuRepository) -> None:
        self._menu_repo = menu_repo

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

        dtos = [
            MenuDTO(
                id=m.id,
                restaurant_id=m.restaurant_id,
                name=m.name,
                description=m.description,
                is_active=m.is_active,
                created_at=m.created_at,
                updated_at=m.updated_at,
                categories=[],
            )
            for m in menus
        ]

        return ListMenusResult(items=dtos, total=total)
