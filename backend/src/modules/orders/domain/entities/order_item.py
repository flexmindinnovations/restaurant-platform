import uuid
from dataclasses import dataclass

from shared.domain.entity import Entity
from shared.domain.value_objects import Money


@dataclass
class OrderItem(Entity):
    order_id: uuid.UUID = None  # type: ignore[assignment]
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

    @classmethod
    def create(
        cls,
        order_id: uuid.UUID,
        menu_item_id: uuid.UUID,
        name: str,
        unit_price: Money,
        quantity: int = 1,
        special_instructions: str | None = None,
    ) -> "OrderItem":
        if quantity < 1:
            raise ValueError("Quantity must be at least 1")
        return cls(
            id=uuid.uuid4(),
            order_id=order_id,
            menu_item_id=menu_item_id,
            name=name,
            unit_price=unit_price,
            quantity=quantity,
            special_instructions=special_instructions,
        )
