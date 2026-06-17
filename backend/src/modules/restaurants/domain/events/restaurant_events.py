import uuid
from dataclasses import dataclass, field

from shared.domain.events import DomainEvent


@dataclass(frozen=True)
class RestaurantRegistered(DomainEvent):
    owner_id: uuid.UUID = field(default_factory=uuid.uuid4)
    name: str = ""


@dataclass(frozen=True)
class RestaurantVerified(DomainEvent):
    pass


@dataclass(frozen=True)
class RestaurantDeactivated(DomainEvent):
    pass
