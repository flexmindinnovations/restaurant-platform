import uuid
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from modules.payments.application.ports.payment_repository import PaymentRepository
from shared.domain.exceptions import ValidationException


@dataclass
class PaymentDTO:
    id: uuid.UUID
    order_id: uuid.UUID
    customer_id: uuid.UUID
    restaurant_id: uuid.UUID
    amount_amount: Decimal
    amount_currency: str
    status: str
    payment_method_type: str
    payment_method_id: uuid.UUID | None
    gateway_transaction_id: str | None
    failure_reason: str | None
    captured_at: datetime | None
    refunded_at: datetime | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, p) -> "PaymentDTO":
        return cls(
            id=p.id,
            order_id=p.order_id,
            customer_id=p.customer_id,
            restaurant_id=p.restaurant_id,
            amount_amount=p.amount.amount,
            amount_currency=p.amount.currency,
            status=p.status,
            payment_method_type=p.payment_method_type,
            payment_method_id=p.payment_method_id,
            gateway_transaction_id=p.gateway_transaction_id,
            failure_reason=p.failure_reason,
            captured_at=p.captured_at,
            refunded_at=p.refunded_at,
            created_at=p.created_at,
            updated_at=p.updated_at,
        )


@dataclass(frozen=True)
class GetPaymentByOrderQuery:
    order_id: uuid.UUID


class GetPaymentByOrderHandler:
    def __init__(self, payment_repo: PaymentRepository) -> None:
        self._payment_repo = payment_repo

    async def handle(self, query: GetPaymentByOrderQuery) -> PaymentDTO:
        p = await self._payment_repo.get_by_order_id(query.order_id)
        if not p:
            raise ValidationException("Payment not found for order")
        return PaymentDTO.from_entity(p)
