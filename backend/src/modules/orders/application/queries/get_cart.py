import uuid
from dataclasses import dataclass
from decimal import Decimal

from modules.orders.application.ports.cart_repository import CartRepository


@dataclass(frozen=True)
class CartItemDTO:
    id: uuid.UUID
    menu_item_id: uuid.UUID
    name: str
    unit_price_amount: Decimal
    unit_price_currency: str
    quantity: int
    special_instructions: str | None
    subtotal_amount: Decimal


@dataclass(frozen=True)
class CartDTO:
    customer_id: uuid.UUID
    restaurant_id: uuid.UUID | None
    items: list[CartItemDTO]
    total_amount: Decimal
    currency: str


@dataclass(frozen=True)
class GetCartQuery:
    customer_id: uuid.UUID


class GetCartHandler:
    def __init__(self, cart_repo: CartRepository) -> None:
        self._cart_repo = cart_repo

    async def handle(self, query: GetCartQuery) -> CartDTO:
        cart = await self._cart_repo.get_by_customer_id(query.customer_id)
        if not cart:
            return CartDTO(
                customer_id=query.customer_id,
                restaurant_id=None,
                items=[],
                total_amount=Decimal("0.00"),
                currency="USD",
            )

        item_dtos = [
            CartItemDTO(
                id=item.id,
                menu_item_id=item.menu_item_id,
                name=item.name,
                unit_price_amount=item.unit_price.amount,
                unit_price_currency=item.unit_price.currency,
                quantity=item.quantity,
                special_instructions=item.special_instructions,
                subtotal_amount=item.subtotal.amount,
            )
            for item in cart.items
        ]

        currency = cart.items[0].unit_price.currency if cart.items else "USD"
        return CartDTO(
            customer_id=cart.id,
            restaurant_id=cart.restaurant_id,
            items=item_dtos,
            total_amount=cart.total_amount.amount,
            currency=currency,
        )
