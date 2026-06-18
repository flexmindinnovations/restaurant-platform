import uuid
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from modules.menus.application.ports.modifier_group_repository import ModifierGroupRepository


@dataclass(frozen=True)
class ModifierDTO:
    id: uuid.UUID
    modifier_group_id: uuid.UUID
    name: str
    price_adjustment_amount: Decimal
    price_adjustment_currency: str
    is_default: bool
    is_available: bool
    display_order: int
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class ModifierGroupDTO:
    id: uuid.UUID
    menu_item_id: uuid.UUID
    restaurant_id: uuid.UUID
    name: str
    description: str | None
    selection_type: str
    min_selections: int
    max_selections: int
    is_required: bool
    display_order: int
    modifiers: list[ModifierDTO]
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class ListModifierGroupsQuery:
    menu_item_id: uuid.UUID


class ListModifierGroupsHandler:
    def __init__(self, group_repo: ModifierGroupRepository) -> None:
        self._group_repo = group_repo

    async def handle(self, query: ListModifierGroupsQuery) -> list[ModifierGroupDTO]:
        groups = await self._group_repo.list_by_menu_item(query.menu_item_id)
        return [
            ModifierGroupDTO(
                id=g.id,
                menu_item_id=g.menu_item_id,
                restaurant_id=g.restaurant_id,
                name=g.name,
                description=g.description,
                selection_type=g.selection_type.value,
                min_selections=g.min_selections,
                max_selections=g.max_selections,
                is_required=g.is_required,
                display_order=g.display_order,
                modifiers=[
                    ModifierDTO(
                        id=m.id,
                        modifier_group_id=m.modifier_group_id,
                        name=m.name,
                        price_adjustment_amount=m.price_adjustment.amount,
                        price_adjustment_currency=m.price_adjustment.currency,
                        is_default=m.is_default,
                        is_available=m.is_available,
                        display_order=m.display_order,
                        created_at=m.created_at,
                        updated_at=m.updated_at,
                    )
                    for m in g.modifiers
                ],
                created_at=g.created_at,
                updated_at=g.updated_at,
            )
            for g in groups
        ]
