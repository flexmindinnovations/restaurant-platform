import uuid
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.menus.application.ports.menu_item_repository import MenuItemRepository
from modules.menus.domain.entities.menu_item import MenuItem
from modules.menus.infrastructure.models.menu_models import MenuItemModel
from shared.domain.value_objects import Money


class SqlAlchemyMenuItemRepository(MenuItemRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, item: MenuItem) -> None:
        model = MenuItemModel(
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
        self._session.add(model)

    async def get_by_id(self, item_id: uuid.UUID) -> MenuItem | None:
        result = await self._session.execute(select(MenuItemModel).where(MenuItemModel.id == item_id))
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_domain(model)

    async def update(self, item: MenuItem) -> None:
        result = await self._session.execute(select(MenuItemModel).where(MenuItemModel.id == item.id))
        model = result.scalar_one_or_none()
        if model:
            model.name = item.name
            model.description = item.description
            model.category_id = item.category_id
            model.price_amount = item.price.amount
            model.price_currency = item.price.currency
            model.image_url = item.image_url
            model.display_order = item.display_order
            model.is_available = item.is_available
            model.dietary_labels = item.dietary_labels
            model.preparation_time_minutes = item.preparation_time_minutes
            model.updated_at = item.updated_at

    async def delete(self, item_id: uuid.UUID) -> None:
        result = await self._session.execute(select(MenuItemModel).where(MenuItemModel.id == item_id))
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)

    async def list_by_menu(
        self,
        menu_id: uuid.UUID,
        category_id: uuid.UUID | None = None,
        available_only: bool = False,
        skip: int = 0,
        limit: int = 50,
    ) -> list[MenuItem]:
        query = select(MenuItemModel).where(MenuItemModel.menu_id == menu_id)
        if category_id is not None:
            query = query.where(MenuItemModel.category_id == category_id)
        if available_only:
            query = query.where(MenuItemModel.is_available.is_(True))
        query = query.order_by(MenuItemModel.display_order).offset(skip).limit(limit)
        result = await self._session.execute(query)
        return [self._to_domain(m) for m in result.scalars().all()]

    async def count_by_menu(
        self,
        menu_id: uuid.UUID,
        category_id: uuid.UUID | None = None,
        available_only: bool = False,
    ) -> int:
        query = select(func.count(MenuItemModel.id)).where(MenuItemModel.menu_id == menu_id)
        if category_id is not None:
            query = query.where(MenuItemModel.category_id == category_id)
        if available_only:
            query = query.where(MenuItemModel.is_available.is_(True))
        result = await self._session.execute(query)
        return result.scalar_one()

    def _to_domain(self, model: MenuItemModel) -> MenuItem:
        return MenuItem(
            id=model.id,
            menu_id=model.menu_id,
            category_id=model.category_id,
            restaurant_id=model.restaurant_id,
            name=model.name,
            description=model.description,
            price=Money(amount=Decimal(str(model.price_amount)), currency=model.price_currency),
            image_url=model.image_url,
            display_order=model.display_order,
            is_available=model.is_available,
            dietary_labels=model.dietary_labels or [],
            preparation_time_minutes=model.preparation_time_minutes,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
