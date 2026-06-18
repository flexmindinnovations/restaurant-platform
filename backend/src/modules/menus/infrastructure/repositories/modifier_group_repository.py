import uuid
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from modules.menus.application.ports.modifier_group_repository import ModifierGroupRepository
from modules.menus.domain.entities.modifier import Modifier, ModifierGroup, SelectionType
from modules.menus.infrastructure.models.menu_models import ModifierGroupModel, ModifierModel
from shared.domain.value_objects import Money


class SqlAlchemyModifierGroupRepository(ModifierGroupRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, group: ModifierGroup) -> None:
        model = ModifierGroupModel(
            id=group.id,
            menu_item_id=group.menu_item_id,
            restaurant_id=group.restaurant_id,
            name=group.name,
            description=group.description,
            selection_type=group.selection_type.value,
            min_selections=group.min_selections,
            max_selections=group.max_selections,
            is_required=group.is_required,
            display_order=group.display_order,
            created_at=group.created_at,
            updated_at=group.updated_at,
        )
        for m in group.modifiers:
            model.modifiers.append(ModifierModel(
                id=m.id,
                modifier_group_id=group.id,
                name=m.name,
                price_adjustment_amount=m.price_adjustment.amount,
                price_adjustment_currency=m.price_adjustment.currency,
                is_default=m.is_default,
                is_available=m.is_available,
                display_order=m.display_order,
                created_at=m.created_at,
                updated_at=m.updated_at,
            ))
        self._session.add(model)

    async def get_by_id(self, group_id: uuid.UUID) -> ModifierGroup | None:
        result = await self._session.execute(
            select(ModifierGroupModel)
            .options(selectinload(ModifierGroupModel.modifiers))
            .where(ModifierGroupModel.id == group_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_domain(model)

    async def update(self, group: ModifierGroup) -> None:
        result = await self._session.execute(
            select(ModifierGroupModel)
            .options(selectinload(ModifierGroupModel.modifiers))
            .where(ModifierGroupModel.id == group.id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return

        model.name = group.name
        model.description = group.description
        model.selection_type = group.selection_type.value
        model.min_selections = group.min_selections
        model.max_selections = group.max_selections
        model.is_required = group.is_required
        model.display_order = group.display_order
        model.updated_at = group.updated_at

        existing_ids = {m.id for m in model.modifiers}
        domain_ids = {m.id for m in group.modifiers}

        for mod_model in list(model.modifiers):
            if mod_model.id not in domain_ids:
                model.modifiers.remove(mod_model)
                await self._session.delete(mod_model)

        for dm in group.modifiers:
            if dm.id in existing_ids:
                for mm in model.modifiers:
                    if mm.id == dm.id:
                        mm.name = dm.name
                        mm.price_adjustment_amount = dm.price_adjustment.amount
                        mm.price_adjustment_currency = dm.price_adjustment.currency
                        mm.is_default = dm.is_default
                        mm.is_available = dm.is_available
                        mm.display_order = dm.display_order
                        mm.updated_at = dm.updated_at
                        break
            else:
                model.modifiers.append(ModifierModel(
                    id=dm.id,
                    modifier_group_id=group.id,
                    name=dm.name,
                    price_adjustment_amount=dm.price_adjustment.amount,
                    price_adjustment_currency=dm.price_adjustment.currency,
                    is_default=dm.is_default,
                    is_available=dm.is_available,
                    display_order=dm.display_order,
                    created_at=dm.created_at,
                    updated_at=dm.updated_at,
                ))

    async def delete(self, group_id: uuid.UUID) -> None:
        result = await self._session.execute(
            select(ModifierGroupModel).where(ModifierGroupModel.id == group_id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)

    async def list_by_menu_item(self, menu_item_id: uuid.UUID) -> list[ModifierGroup]:
        result = await self._session.execute(
            select(ModifierGroupModel)
            .options(selectinload(ModifierGroupModel.modifiers))
            .where(ModifierGroupModel.menu_item_id == menu_item_id)
            .order_by(ModifierGroupModel.display_order)
        )
        return [self._to_domain(m) for m in result.scalars().all()]

    def _to_domain(self, model: ModifierGroupModel) -> ModifierGroup:
        modifiers = [
            Modifier(
                id=m.id,
                modifier_group_id=m.modifier_group_id,
                name=m.name,
                price_adjustment=Money(
                    amount=Decimal(str(m.price_adjustment_amount)),
                    currency=m.price_adjustment_currency,
                ),
                is_default=m.is_default,
                is_available=m.is_available,
                display_order=m.display_order,
                created_at=m.created_at,
                updated_at=m.updated_at,
            )
            for m in sorted(model.modifiers, key=lambda x: x.display_order)
        ]
        return ModifierGroup(
            id=model.id,
            menu_item_id=model.menu_item_id,
            restaurant_id=model.restaurant_id,
            name=model.name,
            description=model.description,
            selection_type=SelectionType(model.selection_type),
            min_selections=model.min_selections,
            max_selections=model.max_selections,
            is_required=model.is_required,
            display_order=model.display_order,
            modifiers=modifiers,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
