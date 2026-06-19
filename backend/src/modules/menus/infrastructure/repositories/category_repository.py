import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.menus.application.ports.category_repository import CategoryRepository
from modules.menus.domain.entities.category import Category
from modules.menus.infrastructure.models.menu_models import CategoryModel


class SqlAlchemyCategoryRepository(CategoryRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, category: Category) -> None:
        model = CategoryModel(
            id=category.id,
            menu_id=category.menu_id,
            name=category.name,
            description=category.description,
            display_order=category.display_order,
            is_active=category.is_active,
            created_at=category.created_at,
            updated_at=category.updated_at,
        )
        self._session.add(model)

    async def get_by_id(self, category_id: uuid.UUID) -> Category | None:
        result = await self._session.execute(select(CategoryModel).where(CategoryModel.id == category_id))
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_domain(model)

    async def update(self, category: Category) -> None:
        result = await self._session.execute(select(CategoryModel).where(CategoryModel.id == category.id))
        model = result.scalar_one_or_none()
        if model:
            model.name = category.name
            model.description = category.description
            model.display_order = category.display_order
            model.is_active = category.is_active
            model.updated_at = category.updated_at

    async def delete(self, category_id: uuid.UUID) -> None:
        result = await self._session.execute(select(CategoryModel).where(CategoryModel.id == category_id))
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)

    async def list_by_menu(self, menu_id: uuid.UUID) -> list[Category]:
        query = select(CategoryModel).where(CategoryModel.menu_id == menu_id).order_by(CategoryModel.display_order)
        result = await self._session.execute(query)
        return [self._to_domain(m) for m in result.scalars().all()]

    def _to_domain(self, model: CategoryModel) -> Category:
        return Category(
            id=model.id,
            menu_id=model.menu_id,
            name=model.name,
            description=model.description,
            display_order=model.display_order,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
