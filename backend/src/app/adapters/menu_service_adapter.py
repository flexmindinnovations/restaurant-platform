import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from modules.menus.infrastructure.repositories.menu_item_repository import SqlAlchemyMenuItemRepository
from modules.orders.application.ports.menu_service import MenuItemDTO, MenuService


class MenuServiceAdapter(MenuService):
    def __init__(self, session: AsyncSession) -> None:
        self._repo = SqlAlchemyMenuItemRepository(session)

    async def get_menu_item(self, menu_item_id: uuid.UUID) -> MenuItemDTO | None:
        item = await self._repo.get_by_id(menu_item_id)
        if not item:
            return None
        return MenuItemDTO(
            id=item.id,
            restaurant_id=item.restaurant_id,
            name=item.name,
            price_amount=item.price.amount,
            price_currency=item.price.currency,
            is_available=item.is_available,
        )
