import uuid
from dataclasses import dataclass, field

from shared.domain.events import DomainEvent


@dataclass(frozen=True)
class ReviewSubmitted(DomainEvent):
    order_id: uuid.UUID = field(default_factory=uuid.uuid4)
    restaurant_id: uuid.UUID = field(default_factory=uuid.uuid4)
    customer_id: uuid.UUID = field(default_factory=uuid.uuid4)
    rating: int = 0


@dataclass(frozen=True)
class ReviewUpdated(DomainEvent):
    rating: int = 0


@dataclass(frozen=True)
class ReviewReplied(DomainEvent):
    restaurant_id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass(frozen=True)
class ReviewFlagged(DomainEvent):
    reason: str = ""
