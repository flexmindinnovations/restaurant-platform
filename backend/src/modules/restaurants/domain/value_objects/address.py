from dataclasses import dataclass

from shared.domain.value_objects import ValueObject


@dataclass(frozen=True)
class Address(ValueObject):
    street: str
    city: str
    state: str
    postal_code: str
    country: str
    latitude: float | None = None
    longitude: float | None = None
