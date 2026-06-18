import uuid
from dataclasses import dataclass, field
from decimal import Decimal

from shared.domain.events import DomainEvent


@dataclass(frozen=True)
class OrderPlaced(DomainEvent):
    restaurant_id: uuid.UUID = field(default_factory=uuid.uuid4)
    customer_id: uuid.UUID = field(default_factory=uuid.uuid4)
    total_amount: Decimal = Decimal("0")


@dataclass(frozen=True)
class OrderConfirmed(DomainEvent):
    pass


@dataclass(frozen=True)
class OrderPreparing(DomainEvent):
    pass


@dataclass(frozen=True)
class OrderReady(DomainEvent):
    pass


@dataclass(frozen=True)
class OrderOutForDelivery(DomainEvent):
    pass


@dataclass(frozen=True)
class OrderDelivered(DomainEvent):
    pass


@dataclass(frozen=True)
class OrderCompleted(DomainEvent):
    pass


@dataclass(frozen=True)
class OrderCancelled(DomainEvent):
    reason: str = ""
