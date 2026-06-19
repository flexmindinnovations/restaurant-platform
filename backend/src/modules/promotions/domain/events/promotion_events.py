import uuid
from dataclasses import dataclass, field
from decimal import Decimal

from shared.domain.events import DomainEvent


@dataclass(frozen=True)
class PromotionCreated(DomainEvent):
    code: str = ""
    promotion_type: str = ""


@dataclass(frozen=True)
class PromotionDeactivated(DomainEvent):
    pass


@dataclass(frozen=True)
class CouponApplied(DomainEvent):
    order_id: uuid.UUID = field(default_factory=uuid.uuid4)
    customer_id: uuid.UUID = field(default_factory=uuid.uuid4)
    discount_amount: Decimal = Decimal("0")
