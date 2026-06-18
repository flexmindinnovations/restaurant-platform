import uuid
from dataclasses import dataclass
from decimal import Decimal

from shared.domain.events import DomainEvent


@dataclass(frozen=True, kw_only=True)
class PaymentAuthorized(DomainEvent):
    payment_id: uuid.UUID
    order_id: uuid.UUID
    amount: Decimal


@dataclass(frozen=True, kw_only=True)
class PaymentCaptured(DomainEvent):
    payment_id: uuid.UUID
    order_id: uuid.UUID
    amount: Decimal


@dataclass(frozen=True, kw_only=True)
class PaymentFailed(DomainEvent):
    payment_id: uuid.UUID
    order_id: uuid.UUID
    reason: str


@dataclass(frozen=True, kw_only=True)
class PaymentRefunded(DomainEvent):
    payment_id: uuid.UUID
    order_id: uuid.UUID
    amount: Decimal
