import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal

from modules.menus.domain.events.menu_events import (
    MenuItemCreated,
    MenuItemRemoved,
    MenuItemUpdated,
)
from shared.domain.entity import AggregateRoot
from shared.domain.exceptions import ValidationException
from shared.domain.value_objects import Money


@dataclass
class MenuItem(AggregateRoot):
    menu_id: uuid.UUID = None  # type: ignore[assignment]
    category_id: uuid.UUID | None = None
    restaurant_id: uuid.UUID = None  # type: ignore[assignment]
    name: str = ""
    description: str | None = None
    price: Money = None  # type: ignore[assignment]
    image_url: str | None = None
    display_order: int = 0
    is_available: bool = True
    dietary_labels: list[str] = field(default_factory=list)
    preparation_time_minutes: int | None = None

    @classmethod
    def create(
        cls,
        menu_id: uuid.UUID,
        restaurant_id: uuid.UUID,
        name: str,
        price: Money,
        category_id: uuid.UUID | None = None,
        description: str | None = None,
        image_url: str | None = None,
        display_order: int = 0,
        dietary_labels: list[str] | None = None,
        preparation_time_minutes: int | None = None,
    ) -> "MenuItem":
        if not name:
            raise ValidationException("Menu item name cannot be empty")
        if price.amount <= 0:
            raise ValidationException("Menu item price must be greater than zero")

        item_id = uuid.uuid4()
        item = cls(
            id=item_id,
            menu_id=menu_id,
            category_id=category_id,
            restaurant_id=restaurant_id,
            name=name,
            description=description,
            price=price,
            image_url=image_url,
            display_order=display_order,
            is_available=True,
            dietary_labels=dietary_labels or [],
            preparation_time_minutes=preparation_time_minutes,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        item.register_event(
            MenuItemCreated(
                aggregate_id=item_id,
                menu_id=menu_id,
                name=name,
            )
        )
        return item

    def update_details(
        self,
        name: str | None = None,
        description: str | None = None,
        price: Money | None = None,
        image_url: str | None = None,
        display_order: int | None = None,
        dietary_labels: list[str] | None = None,
        preparation_time_minutes: int | None = None,
        category_id: uuid.UUID | None = ...,  # type: ignore[assignment]
    ) -> None:
        if name is not None:
            if not name:
                raise ValidationException("Menu item name cannot be empty")
            self.name = name
        if description is not None:
            self.description = description
        if price is not None:
            if price.amount <= 0:
                raise ValidationException("Menu item price must be greater than zero")
            self.price = price
        if image_url is not None:
            self.image_url = image_url
        if display_order is not None:
            self.display_order = display_order
        if dietary_labels is not None:
            self.dietary_labels = dietary_labels
        if preparation_time_minutes is not None:
            self.preparation_time_minutes = preparation_time_minutes
        if category_id is not ...:
            self.category_id = category_id
        self.updated_at = datetime.now(UTC)
        self.register_event(MenuItemUpdated(aggregate_id=self.id))

    def set_availability(self, available: bool) -> None:
        self.is_available = available
        self.updated_at = datetime.now(UTC)
        self.register_event(MenuItemUpdated(aggregate_id=self.id))

    def mark_removed(self) -> None:
        self.is_available = False
        self.updated_at = datetime.now(UTC)
        self.register_event(MenuItemRemoved(aggregate_id=self.id))

    def change_price(self, new_amount: Decimal, currency: str | None = None) -> None:
        self.price = Money(
            amount=new_amount,
            currency=currency or self.price.currency,
        )
        self.updated_at = datetime.now(UTC)
        self.register_event(MenuItemUpdated(aggregate_id=self.id))
