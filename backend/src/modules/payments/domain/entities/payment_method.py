import uuid
from dataclasses import dataclass

from shared.domain.entity import AggregateRoot


@dataclass
class PaymentMethod(AggregateRoot):
    customer_id: uuid.UUID = None  # type: ignore[assignment]
    type: str = "CARD"
    last_four: str | None = None
    brand: str | None = None
    is_default: bool = False
    token: str = ""
