import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal

from shared.domain.entity import AggregateRoot, Entity
from shared.domain.exceptions import ValidationException
from shared.domain.value_objects import Money


@dataclass
class CartItem(Entity):
    menu_item_id: uuid.UUID = None  # type: ignore[assignment]
    name: str = ""
    unit_price: Money = None  # type: ignore[assignment]
    quantity: int = 1
    special_instructions: str | None = None

    @property
    def subtotal(self) -> Money:
        return Money(
            amount=self.unit_price.amount * self.quantity,
            currency=self.unit_price.currency,
        )

    def change_quantity(self, quantity: int) -> None:
        if quantity < 1:
            raise ValidationException("Quantity must be at least 1")
        self.quantity = quantity


@dataclass
class Cart(AggregateRoot):
    restaurant_id: uuid.UUID | None = None
    items: list[CartItem] = field(default_factory=list)

    @classmethod
    def create(cls, customer_id: uuid.UUID) -> "Cart":
        now = datetime.now(UTC)
        return cls(
            id=customer_id,
            restaurant_id=None,
            items=[],
            created_at=now,
            updated_at=now,
        )

    def add_item(
        self,
        menu_item_id: uuid.UUID,
        name: str,
        unit_price: Money,
        restaurant_id: uuid.UUID,
        quantity: int = 1,
        special_instructions: str | None = None,
    ) -> None:
        if quantity < 1:
            raise ValidationException("Quantity must be at least 1")

        if self.restaurant_id is not None and self.restaurant_id != restaurant_id:
            raise ValidationException("Cannot add items from a different restaurant to the cart")

        if self.restaurant_id is None:
            self.restaurant_id = restaurant_id

        # Check if identical item (same ID and same instructions) already exists
        for item in self.items:
            if item.menu_item_id == menu_item_id and item.special_instructions == special_instructions:
                item.change_quantity(item.quantity + quantity)
                self.updated_at = datetime.now(UTC)
                return

        # Otherwise, create a new item
        new_item = CartItem(
            id=uuid.uuid4(),
            menu_item_id=menu_item_id,
            name=name,
            unit_price=unit_price,
            quantity=quantity,
            special_instructions=special_instructions,
        )
        self.items.append(new_item)
        self.updated_at = datetime.now(UTC)

    def remove_item(self, menu_item_id: uuid.UUID) -> None:
        self.items = [item for item in self.items if item.menu_item_id != menu_item_id]
        if not self.items:
            self.restaurant_id = None
        self.updated_at = datetime.now(UTC)

    def update_quantity(self, menu_item_id: uuid.UUID, quantity: int) -> None:
        if quantity <= 0:
            self.remove_item(menu_item_id)
            return

        for item in self.items:
            if item.menu_item_id == menu_item_id:
                item.change_quantity(quantity)
                self.updated_at = datetime.now(UTC)
                return

        raise ValidationException("Item not found in cart")

    def clear(self) -> None:
        self.items = []
        self.restaurant_id = None
        self.updated_at = datetime.now(UTC)

    @property
    def total_amount(self) -> Money:
        if not self.items:
            return Money(amount=Decimal("0"))
        currency = self.items[0].unit_price.currency
        total_amount = sum((item.subtotal.amount for item in self.items), Decimal("0"))
        return Money(amount=total_amount, currency=currency)
