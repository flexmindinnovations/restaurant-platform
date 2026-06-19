import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal

from shared.domain.entity import Entity


@dataclass
class CouponUsage(Entity):
    promotion_id: uuid.UUID = None  # type: ignore[assignment]
    order_id: uuid.UUID = None  # type: ignore[assignment]
    customer_id: uuid.UUID = None  # type: ignore[assignment]
    discount_amount: Decimal = Decimal("0")
    discount_currency: str = "USD"

    @classmethod
    def record(
        cls,
        promotion_id: uuid.UUID,
        order_id: uuid.UUID,
        customer_id: uuid.UUID,
        discount_amount: Decimal,
        discount_currency: str = "USD",
    ) -> "CouponUsage":
        now = datetime.now(UTC)
        return cls(
            id=uuid.uuid4(),
            promotion_id=promotion_id,
            order_id=order_id,
            customer_id=customer_id,
            discount_amount=discount_amount,
            discount_currency=discount_currency,
            created_at=now,
            updated_at=now,
        )
