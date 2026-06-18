import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from modules.payments.domain.events.payment_events import (
    PaymentAuthorized,
    PaymentCaptured,
    PaymentFailed,
    PaymentRefunded,
)
from modules.payments.domain.value_objects.payment_status import PaymentStatus
from shared.domain.entity import AggregateRoot
from shared.domain.exceptions import ValidationException
from shared.domain.value_objects import Money

_VALID_TRANSITIONS: dict[PaymentStatus, set[PaymentStatus]] = {
    PaymentStatus.PENDING: {PaymentStatus.AUTHORIZED, PaymentStatus.FAILED},
    PaymentStatus.AUTHORIZED: {PaymentStatus.CAPTURED, PaymentStatus.VOIDED},
    PaymentStatus.CAPTURED: {PaymentStatus.REFUNDED},
    PaymentStatus.REFUNDED: {PaymentStatus.REFUNDED},  # Support subsequent partial refunds
    PaymentStatus.FAILED: set(),
    PaymentStatus.VOIDED: set(),
}


@dataclass
class Payment(AggregateRoot):
    order_id: uuid.UUID = None  # type: ignore[assignment]
    customer_id: uuid.UUID = None  # type: ignore[assignment]
    restaurant_id: uuid.UUID = None  # type: ignore[assignment]
    amount: Money = None  # type: ignore[assignment]
    status: PaymentStatus = PaymentStatus.PENDING
    payment_method_type: str = "CARD"
    payment_method_id: uuid.UUID | None = None
    gateway_transaction_id: str | None = None
    gateway_response: dict[str, Any] | None = field(default_factory=dict)
    failure_reason: str | None = None
    captured_at: datetime | None = None
    refunded_at: datetime | None = None

    @classmethod
    def initiate(
        cls,
        order_id: uuid.UUID,
        customer_id: uuid.UUID,
        restaurant_id: uuid.UUID,
        amount: Money,
        payment_method_type: str = "CARD",
        payment_method_id: uuid.UUID | None = None,
    ) -> "Payment":
        now = datetime.now(UTC)
        return cls(
            id=uuid.uuid4(),
            order_id=order_id,
            customer_id=customer_id,
            restaurant_id=restaurant_id,
            amount=amount,
            status=PaymentStatus.PENDING,
            payment_method_type=payment_method_type,
            payment_method_id=payment_method_id,
            created_at=now,
            updated_at=now,
        )

    def transition_to(self, new_status: PaymentStatus) -> None:
        allowed = _VALID_TRANSITIONS.get(self.status, set())
        if new_status not in allowed:
            raise ValidationException(
                f"Cannot transition payment from {self.status} to {new_status}"
            )
        self.status = new_status
        self.updated_at = datetime.now(UTC)

    def authorize(self, gateway_transaction_id: str, response: dict[str, Any]) -> None:
        self.transition_to(PaymentStatus.AUTHORIZED)
        self.gateway_transaction_id = gateway_transaction_id
        self.gateway_response = response
        self.register_event(
            PaymentAuthorized(
                aggregate_id=self.id,
                payment_id=self.id,
                order_id=self.order_id,
                amount=self.amount.amount,
            )
        )

    def capture(self, response: dict[str, Any]) -> None:
        self.transition_to(PaymentStatus.CAPTURED)
        self.gateway_response = response
        self.captured_at = datetime.now(UTC)
        self.register_event(
            PaymentCaptured(
                aggregate_id=self.id,
                payment_id=self.id,
                order_id=self.order_id,
                amount=self.amount.amount,
            )
        )

    def void(self, response: dict[str, Any]) -> None:
        self.transition_to(PaymentStatus.VOIDED)
        self.gateway_response = response

    def refund(self, refund_amount: Decimal, response: dict[str, Any]) -> None:
        if refund_amount <= Decimal("0") or refund_amount > self.amount.amount:
            raise ValidationException("Invalid refund amount")
        self.transition_to(PaymentStatus.REFUNDED)
        self.gateway_response = response
        self.refunded_at = datetime.now(UTC)
        self.register_event(
            PaymentRefunded(
                aggregate_id=self.id,
                payment_id=self.id,
                order_id=self.order_id,
                amount=refund_amount,
            )
        )

    def fail(self, reason: str, response: dict[str, Any]) -> None:
        self.transition_to(PaymentStatus.FAILED)
        self.failure_reason = reason
        self.gateway_response = response
        self.register_event(
            PaymentFailed(
                aggregate_id=self.id,
                payment_id=self.id,
                order_id=self.order_id,
                reason=reason,
            )
        )
