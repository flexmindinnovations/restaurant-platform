import uuid
from dataclasses import dataclass
from decimal import Decimal

from modules.menus.application.ports.menu_item_repository import MenuItemRepository
from modules.menus.application.ports.modifier_group_repository import ModifierGroupRepository
from modules.menus.domain.entities.modifier import ModifierGroup, SelectionType
from shared.application.ports.unit_of_work import AbstractUnitOfWork
from shared.domain.exceptions import NotFoundException
from shared.domain.value_objects import Money

# --- Create ModifierGroup ---


@dataclass(frozen=True)
class CreateModifierGroupCommand:
    menu_item_id: uuid.UUID
    restaurant_id: uuid.UUID
    name: str
    selection_type: str = "SINGLE"
    min_selections: int = 0
    max_selections: int = 1
    is_required: bool = False
    description: str | None = None
    display_order: int = 0


class CreateModifierGroupHandler:
    def __init__(
        self,
        item_repo: MenuItemRepository,
        group_repo: ModifierGroupRepository,
        uow: AbstractUnitOfWork,
    ) -> None:
        self._item_repo = item_repo
        self._group_repo = group_repo
        self._uow = uow

    async def handle(self, command: CreateModifierGroupCommand) -> uuid.UUID:
        item = await self._item_repo.get_by_id(command.menu_item_id)
        if not item:
            raise NotFoundException("Menu item not found")

        group = ModifierGroup.create(
            menu_item_id=command.menu_item_id,
            restaurant_id=command.restaurant_id,
            name=command.name,
            selection_type=SelectionType(command.selection_type),
            min_selections=command.min_selections,
            max_selections=command.max_selections,
            is_required=command.is_required,
            description=command.description,
            display_order=command.display_order,
        )

        async with self._uow:
            await self._group_repo.add(group)
            await self._uow.commit()

        return group.id


# --- Add Modifier to Group ---


@dataclass(frozen=True)
class AddModifierCommand:
    modifier_group_id: uuid.UUID
    name: str
    price_adjustment_amount: Decimal = Decimal("0.00")
    price_adjustment_currency: str = "INR"
    is_default: bool = False
    display_order: int = 0


class AddModifierHandler:
    def __init__(
        self,
        group_repo: ModifierGroupRepository,
        uow: AbstractUnitOfWork,
    ) -> None:
        self._group_repo = group_repo
        self._uow = uow

    async def handle(self, command: AddModifierCommand) -> uuid.UUID:
        group = await self._group_repo.get_by_id(command.modifier_group_id)
        if not group:
            raise NotFoundException("Modifier group not found")

        modifier = group.add_modifier(
            name=command.name,
            price_adjustment=Money(command.price_adjustment_amount, command.price_adjustment_currency),
            is_default=command.is_default,
            display_order=command.display_order,
        )

        async with self._uow:
            await self._group_repo.update(group)
            await self._uow.commit()

        return modifier.id


# --- Delete ModifierGroup ---


@dataclass(frozen=True)
class DeleteModifierGroupCommand:
    modifier_group_id: uuid.UUID


class DeleteModifierGroupHandler:
    def __init__(
        self,
        group_repo: ModifierGroupRepository,
        uow: AbstractUnitOfWork,
    ) -> None:
        self._group_repo = group_repo
        self._uow = uow

    async def handle(self, command: DeleteModifierGroupCommand) -> None:
        async with self._uow:
            await self._group_repo.delete(command.modifier_group_id)
            await self._uow.commit()


# --- Remove Modifier from Group ---


@dataclass(frozen=True)
class RemoveModifierCommand:
    modifier_group_id: uuid.UUID
    modifier_id: uuid.UUID


class RemoveModifierHandler:
    def __init__(
        self,
        group_repo: ModifierGroupRepository,
        uow: AbstractUnitOfWork,
    ) -> None:
        self._group_repo = group_repo
        self._uow = uow

    async def handle(self, command: RemoveModifierCommand) -> None:
        group = await self._group_repo.get_by_id(command.modifier_group_id)
        if not group:
            raise NotFoundException("Modifier group not found")

        group.remove_modifier(command.modifier_id)

        async with self._uow:
            await self._group_repo.update(group)
            await self._uow.commit()
