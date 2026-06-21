import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.menus.application.ports.menu_repository import MenuRepository
from modules.menus.domain.entities.menu import Menu
from modules.menus.infrastructure.models.menu_models import MenuModel


class SqlAlchemyMenuRepository(MenuRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, menu: Menu) -> None:
        model = MenuModel(
            id=menu.id,
            restaurant_id=menu.restaurant_id,
            name=menu.name,
            description=menu.description,
            is_active=menu.is_active,
            created_at=menu.created_at,
            updated_at=menu.updated_at,
        )
        self._session.add(model)

    async def get_by_id(self, menu_id: uuid.UUID) -> Menu | None:
        result = await self._session.execute(select(MenuModel).where(MenuModel.id == menu_id))
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_domain(model)

    async def update(self, menu: Menu) -> None:
        result = await self._session.execute(select(MenuModel).where(MenuModel.id == menu.id))
        model = result.scalar_one_or_none()
        if model:
            model.name = menu.name
            model.description = menu.description
            model.is_active = menu.is_active
            model.updated_at = menu.updated_at

    async def delete(self, menu_id: uuid.UUID) -> None:
        result = await self._session.execute(select(MenuModel).where(MenuModel.id == menu_id))
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)

    async def list_by_restaurant(
        self,
        restaurant_id: uuid.UUID,
        skip: int = 0,
        limit: int = 20,
        active_only: bool = False,
    ) -> list[Menu]:
        query = select(MenuModel).where(MenuModel.restaurant_id == restaurant_id)
        if active_only:
            query = query.where(MenuModel.is_active.is_(True))
        query = query.order_by(MenuModel.created_at.desc()).offset(skip).limit(limit)
        result = await self._session.execute(query)
        return [self._to_domain(m) for m in result.scalars().all()]

    async def count_by_restaurant(
        self,
        restaurant_id: uuid.UUID,
        active_only: bool = False,
    ) -> int:
        query = select(func.count(MenuModel.id)).where(MenuModel.restaurant_id == restaurant_id)
        if active_only:
            query = query.where(MenuModel.is_active.is_(True))
        result = await self._session.execute(query)
        return result.scalar_one()

    async def exists_by_name(self, restaurant_id: uuid.UUID, name: str) -> bool:
        query = select(func.count(MenuModel.id)).where(
            MenuModel.restaurant_id == restaurant_id,
            func.lower(MenuModel.name) == name.lower(),
        )
        result = await self._session.execute(query)
        return result.scalar_one() > 0

    def _to_domain(self, model: MenuModel) -> Menu:
        return Menu(
            id=model.id,
            restaurant_id=model.restaurant_id,
            name=model.name,
            description=model.description,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
