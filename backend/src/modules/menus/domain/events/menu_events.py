import uuid
from dataclasses import dataclass, field

from shared.domain.events import DomainEvent


@dataclass(frozen=True)
class MenuCreated(DomainEvent):
    restaurant_id: uuid.UUID = field(default_factory=uuid.uuid4)
    name: str = ""


@dataclass(frozen=True)
class MenuUpdated(DomainEvent):
    pass


@dataclass(frozen=True)
class MenuPublished(DomainEvent):
    pass


@dataclass(frozen=True)
class MenuUnpublished(DomainEvent):
    pass


@dataclass(frozen=True)
class MenuItemCreated(DomainEvent):
    menu_id: uuid.UUID = field(default_factory=uuid.uuid4)
    name: str = ""


@dataclass(frozen=True)
class MenuItemUpdated(DomainEvent):
    pass


@dataclass(frozen=True)
class MenuItemRemoved(DomainEvent):
    pass
