import uuid
from dataclasses import dataclass
from decimal import Decimal

from modules.menus.application.ports.menu_item_repository import MenuItemRepository
from modules.menus.application.ports.menu_repository import MenuRepository
from modules.menus.domain.entities.menu_item import MenuItem
from shared.application.ports.unit_of_work import AbstractUnitOfWork
from shared.domain.exceptions import BusinessRuleViolationError, NotFoundException
from shared.domain.value_objects import Money


@dataclass(frozen=True)
class CreateMenuItemCommand:
    menu_id: uuid.UUID
    restaurant_id: uuid.UUID
    name: str
    price_amount: Decimal
    price_currency: str = "INR"
    category_id: uuid.UUID | None = None
    description: str | None = None
    image_url: str | None = None
    display_order: int = 0
    dietary_labels: list[str] | None = None
    preparation_time_minutes: int | None = None


class CreateMenuItemHandler:
    def __init__(
        self,
        menu_repo: MenuRepository,
        item_repo: MenuItemRepository,
        uow: AbstractUnitOfWork,
    ) -> None:
        self._menu_repo = menu_repo
        self._item_repo = item_repo
        self._uow = uow

    async def handle(self, command: CreateMenuItemCommand) -> uuid.UUID:
        async with self._uow:
            menu = await self._menu_repo.get_by_id(command.menu_id)
            if not menu:
                raise NotFoundException("Menu not found")

            if await self._item_repo.exists_by_name(command.menu_id, command.name, command.category_id):
                raise BusinessRuleViolationError(f'A menu item named "{command.name}" already exists in this category')

            price = Money(amount=command.price_amount, currency=command.price_currency)
            item = MenuItem.create(
                menu_id=command.menu_id,
                restaurant_id=command.restaurant_id,
                name=command.name,
                price=price,
                category_id=command.category_id,
                description=command.description,
                image_url=command.image_url,
                display_order=command.display_order,
                dietary_labels=command.dietary_labels,
                preparation_time_minutes=command.preparation_time_minutes,
            )
            await self._item_repo.add(item)
            self._uow.register_aggregate(item)
            await self._uow.commit()

        return item.id


@dataclass(frozen=True)
class UpdateMenuItemCommand:
    item_id: uuid.UUID
    name: str | None = None
    description: str | None = None
    price_amount: Decimal | None = None
    price_currency: str | None = None
    image_url: str | None = None
    display_order: int | None = None
    is_available: bool | None = None
    dietary_labels: list[str] | None = None
    preparation_time_minutes: int | None = None
    category_id: uuid.UUID | None = ...  # type: ignore[assignment]


class UpdateMenuItemHandler:
    def __init__(self, item_repo: MenuItemRepository, uow: AbstractUnitOfWork) -> None:
        self._item_repo = item_repo
        self._uow = uow

    async def handle(self, command: UpdateMenuItemCommand) -> None:
        async with self._uow:
            item = await self._item_repo.get_by_id(command.item_id)
            if not item:
                raise NotFoundException("Menu item not found")

            new_price = None
            if command.price_amount is not None:
                new_price = Money(
                    amount=command.price_amount,
                    currency=command.price_currency or item.price.currency,
                )

            item.update_details(
                name=command.name,
                description=command.description,
                price=new_price,
                image_url=command.image_url,
                display_order=command.display_order,
                dietary_labels=command.dietary_labels,
                preparation_time_minutes=command.preparation_time_minutes,
                category_id=command.category_id,
            )

            if command.is_available is not None:
                item.set_availability(command.is_available)

            await self._item_repo.update(item)
            self._uow.register_aggregate(item)
            await self._uow.commit()


@dataclass(frozen=True)
class DeleteMenuItemCommand:
    item_id: uuid.UUID


class DeleteMenuItemHandler:
    def __init__(self, item_repo: MenuItemRepository, uow: AbstractUnitOfWork) -> None:
        self._item_repo = item_repo
        self._uow = uow

    async def handle(self, command: DeleteMenuItemCommand) -> None:
        async with self._uow:
            item = await self._item_repo.get_by_id(command.item_id)
            if not item:
                raise NotFoundException("Menu item not found")

            await self._item_repo.delete(command.item_id)
            await self._uow.commit()
