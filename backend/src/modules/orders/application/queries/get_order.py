import uuid
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from modules.orders.application.ports.order_repository import OrderRepository
from shared.domain.exceptions import NotFoundException


@dataclass(frozen=True)
class OrderItemDTO:
    id: uuid.UUID
    menu_item_id: uuid.UUID
    name: str
    unit_price_amount: Decimal
    unit_price_currency: str
    quantity: int
    special_instructions: str | None
    subtotal_amount: Decimal


@dataclass(frozen=True)
class OrderDTO:
    id: uuid.UUID
    restaurant_id: uuid.UUID
    customer_id: uuid.UUID
    order_number: str
    status: str
    delivery_address_street: str
    delivery_address_city: str
    delivery_address_state: str
    delivery_address_postal_code: str
    delivery_address_country: str
    delivery_notes: str | None
    subtotal_amount: Decimal
    subtotal_currency: str
    tax_amount: Decimal
    tax_currency: str
    delivery_fee_amount: Decimal
    delivery_fee_currency: str
    tip_amount: Decimal
    tip_currency: str
    total_amount: Decimal
    total_currency: str
    cancellation_reason: str | None
    placed_at: datetime
    confirmed_at: datetime | None
    preparing_at: datetime | None
    ready_at: datetime | None
    picked_up_at: datetime | None
    delivered_at: datetime | None
    cancelled_at: datetime | None
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemDTO]


@dataclass(frozen=True)
class GetOrderQuery:
    order_id: uuid.UUID


class GetOrderHandler:
    def __init__(self, order_repo: OrderRepository) -> None:
        self._order_repo = order_repo

    async def handle(self, query: GetOrderQuery) -> OrderDTO:
        order = await self._order_repo.get_by_id(query.order_id)
        if not order:
            raise NotFoundException("Order not found")

        item_dtos = [
            OrderItemDTO(
                id=item.id,
                menu_item_id=item.menu_item_id,
                name=item.name,
                unit_price_amount=item.unit_price.amount,
                unit_price_currency=item.unit_price.currency,
                quantity=item.quantity,
                special_instructions=item.special_instructions,
                subtotal_amount=item.subtotal.amount,
            )
            for item in order.items
        ]

        return OrderDTO(
            id=order.id,
            restaurant_id=order.restaurant_id,
            customer_id=order.customer_id,
            order_number=order.order_number.value,
            status=order.status.value,
            delivery_address_street=order.delivery_address_street,
            delivery_address_city=order.delivery_address_city,
            delivery_address_state=order.delivery_address_state,
            delivery_address_postal_code=order.delivery_address_postal_code,
            delivery_address_country=order.delivery_address_country,
            delivery_notes=order.delivery_notes,
            subtotal_amount=order.subtotal.amount,
            subtotal_currency=order.subtotal.currency,
            tax_amount=order.tax.amount,
            tax_currency=order.tax.currency,
            delivery_fee_amount=order.delivery_fee.amount,
            delivery_fee_currency=order.delivery_fee.currency,
            tip_amount=order.tip.amount,
            tip_currency=order.tip.currency,
            total_amount=order.total_amount.amount,
            total_currency=order.total_amount.currency,
            cancellation_reason=order.cancellation_reason,
            placed_at=order.placed_at,
            confirmed_at=order.confirmed_at,
            preparing_at=order.preparing_at,
            ready_at=order.ready_at,
            picked_up_at=order.picked_up_at,
            delivered_at=order.delivered_at,
            cancelled_at=order.cancelled_at,
            created_at=order.created_at,
            updated_at=order.updated_at,
            items=item_dtos,
        )
