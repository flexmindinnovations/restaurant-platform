import uuid
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class ValueObject:
    """Base class for all value objects."""


@dataclass(frozen=True)
class Money(ValueObject):
    amount: Decimal
    currency: str = "USD"

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError("Money amount cannot be negative")

    def add(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError(f"Cannot add {self.currency} and {other.currency}")
        return Money(amount=self.amount + other.amount, currency=self.currency)

    def subtract(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError(f"Cannot subtract {self.currency} and {other.currency}")
        return Money(amount=self.amount - other.amount, currency=self.currency)


@dataclass(frozen=True)
class Address(ValueObject):
    street: str
    city: str
    state: str
    postal_code: str
    country: str
    latitude: float | None = None
    longitude: float | None = None


@dataclass(frozen=True)
class PhoneNumber(ValueObject):
    country_code: str
    number: str

    @property
    def full_number(self) -> str:
        return f"+{self.country_code}{self.number}"


@dataclass(frozen=True)
class EntityReference(ValueObject):
    """Soft reference to an entity in another bounded context."""

    id: uuid.UUID
    entity_type: str
