import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime

from modules.orders.domain.entities.order_item import OrderItem
from modules.orders.domain.events.order_events import (
    OrderCancelled,
    OrderCompleted,
    OrderConfirmed,
    OrderDelivered,
    OrderOutForDelivery,
    OrderPlaced,
    OrderPreparing,
    OrderReady,
)
from modules.orders.domain.value_objects.order_number import OrderNumber
from modules.orders.domain.value_objects.order_status import OrderStatus
from shared.domain.entity import AggregateRoot
from shared.domain.exceptions import ValidationException
from shared.domain.value_objects import Money

_VALID_TRANSITIONS: dict[OrderStatus, set[OrderStatus]] = {
    OrderStatus.PENDING: {OrderStatus.CONFIRMED, OrderStatus.CANCELLED},
    OrderStatus.CONFIRMED: {OrderStatus.PREPARING, OrderStatus.CANCELLED},
    OrderStatus.PREPARING: {OrderStatus.READY},
    OrderStatus.READY: {OrderStatus.OUT_FOR_DELIVERY, OrderStatus.COMPLETED},
    OrderStatus.OUT_FOR_DELIVERY: {OrderStatus.DELIVERED},
    OrderStatus.DELIVERED: {OrderStatus.COMPLETED},
    OrderStatus.COMPLETED: set(),
    OrderStatus.CANCELLED: set(),
}

_STATUS_EVENTS = {
    OrderStatus.CONFIRMED: OrderConfirmed,
    OrderStatus.PREPARING: OrderPreparing,
    OrderStatus.READY: OrderReady,
    OrderStatus.OUT_FOR_DELIVERY: OrderOutForDelivery,
    OrderStatus.DELIVERED: OrderDelivered,
    OrderStatus.COMPLETED: OrderCompleted,
}


@dataclass
class Order(AggregateRoot):
    restaurant_id: uuid.UUID = None  # type: ignore[assignment]
    customer_id: uuid.UUID = None  # type: ignore[assignment]
    order_number: OrderNumber = None  # type: ignore[assignment]
    status: OrderStatus = OrderStatus.PENDING
    items: list[OrderItem] = field(default_factory=list)
    delivery_address_street: str = ""
    delivery_address_city: str = ""
    delivery_address_state: str = ""
    delivery_address_postal_code: str = ""
    delivery_address_country: str = ""
    delivery_notes: str | None = None
    subtotal: Money = None  # type: ignore[assignment]
    tax: Money = None  # type: ignore[assignment]
    delivery_fee: Money = None  # type: ignore[assignment]
    tip: Money = None  # type: ignore[assignment]
    total_amount: Money = None  # type: ignore[assignment]
    cancellation_reason: str | None = None
    placed_at: datetime = None  # type: ignore[assignment]
    confirmed_at: datetime | None = None
    preparing_at: datetime | None = None
    ready_at: datetime | None = None
    picked_up_at: datetime | None = None
    delivered_at: datetime | None = None
    cancelled_at: datetime | None = None

    @classmethod
    def place(
        cls,
        restaurant_id: uuid.UUID,
        customer_id: uuid.UUID,
        items: list[OrderItem],
        delivery_address_street: str,
        delivery_address_city: str,
        delivery_address_state: str,
        delivery_address_postal_code: str,
        delivery_address_country: str,
        subtotal: Money,
        tax: Money,
        delivery_fee: Money,
        tip: Money,
        delivery_notes: str | None = None,
    ) -> "Order":
        if not items:
            raise ValidationException("Order must have at least one item")

        # Validate currency consistency
        currency = subtotal.currency
        for item in items:
            if item.unit_price.currency != currency:
                raise ValidationException("All items must have the same currency")
        if tax.currency != currency or delivery_fee.currency != currency or tip.currency != currency:
            raise ValidationException("All charge amounts must have the same currency")

        total_amount = Money(
            amount=subtotal.amount + tax.amount + delivery_fee.amount + tip.amount,
            currency=currency,
        )

        order_id = uuid.uuid4()
        order_number = OrderNumber.generate()
        now = datetime.now(UTC)

        order = cls(
            id=order_id,
            restaurant_id=restaurant_id,
            customer_id=customer_id,
            order_number=order_number,
            status=OrderStatus.PENDING,
            items=items,
            delivery_address_street=delivery_address_street,
            delivery_address_city=delivery_address_city,
            delivery_address_state=delivery_address_state,
            delivery_address_postal_code=delivery_address_postal_code,
            delivery_address_country=delivery_address_country,
            delivery_notes=delivery_notes,
            subtotal=subtotal,
            tax=tax,
            delivery_fee=delivery_fee,
            tip=tip,
            total_amount=total_amount,
            cancellation_reason=None,
            placed_at=now,
            created_at=now,
            updated_at=now,
        )

        order.register_event(
            OrderPlaced(
                aggregate_id=order_id,
                restaurant_id=restaurant_id,
                customer_id=customer_id,
                total_amount=total_amount.amount,
            )
        )
        return order

    def transition_to(self, new_status: OrderStatus) -> None:
        allowed = _VALID_TRANSITIONS.get(self.status, set())
        if new_status not in allowed:
            raise ValidationException(f"Cannot transition from {self.status} to {new_status}")

        now = datetime.now(UTC)
        self.status = new_status
        self.updated_at = now

        if new_status == OrderStatus.CONFIRMED:
            self.confirmed_at = now
        elif new_status == OrderStatus.PREPARING:
            self.preparing_at = now
        elif new_status == OrderStatus.READY:
            self.ready_at = now
        elif new_status == OrderStatus.OUT_FOR_DELIVERY:
            self.picked_up_at = now
        elif new_status == OrderStatus.DELIVERED:
            self.delivered_at = now
        elif new_status == OrderStatus.COMPLETED:
            # If not already set, populate transit markers
            pass

        event_cls = _STATUS_EVENTS.get(new_status)
        if event_cls:
            self.register_event(event_cls(aggregate_id=self.id))

    def confirm(self) -> None:
        self.transition_to(OrderStatus.CONFIRMED)

    def start_preparing(self) -> None:
        self.transition_to(OrderStatus.PREPARING)

    def mark_ready(self) -> None:
        self.transition_to(OrderStatus.READY)

    def mark_picked_up(self) -> None:
        self.transition_to(OrderStatus.OUT_FOR_DELIVERY)

    def mark_delivered(self) -> None:
        self.transition_to(OrderStatus.DELIVERED)

    def complete(self) -> None:
        self.transition_to(OrderStatus.COMPLETED)

    def cancel(self, reason: str = "") -> None:
        if not self.status.is_cancellable:
            raise ValidationException(f"Cannot cancel order in {self.status} status")
        now = datetime.now(UTC)
        self.status = OrderStatus.CANCELLED
        self.cancellation_reason = reason
        self.cancelled_at = now
        self.updated_at = now
        self.register_event(OrderCancelled(aggregate_id=self.id, reason=reason))
