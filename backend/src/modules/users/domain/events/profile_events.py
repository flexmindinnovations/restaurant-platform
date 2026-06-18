import uuid
from dataclasses import dataclass, field

from shared.domain.events import DomainEvent


@dataclass(frozen=True)
class ProfileCreated(DomainEvent):
    account_id: uuid.UUID = field(default_factory=uuid.uuid4)
    first_name: str = ""
    last_name: str = ""


@dataclass(frozen=True)
class ProfileUpdated(DomainEvent):
    pass
