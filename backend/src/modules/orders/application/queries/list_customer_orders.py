import uuid
from dataclasses import dataclass

from modules.orders.application.ports.order_repository import OrderRepository
from modules.orders.application.queries.get_order import OrderDTO, OrderItemDTO


@dataclass(frozen=True)
class ListCustomerOrdersQuery:
    customer_id: uuid.UUID
    skip: int = 0
    limit: int = 10


@dataclass(frozen=True)
class CustomerOrdersListDTO:
    items: list[OrderDTO]
    total: int


class ListCustomerOrdersHandler:
    def __init__(self, order_repo: OrderRepository) -> None:
        self._order_repo = order_repo

    async def handle(self, query: ListCustomerOrdersQuery) -> CustomerOrdersListDTO:
        orders, total = await self._order_repo.list_by_customer(
            query.customer_id, skip=query.skip, limit=query.limit
        )

        dtos = []
        for order in orders:
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
            dtos.append(
                OrderDTO(
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
            )

        return CustomerOrdersListDTO(items=dtos, total=total)
