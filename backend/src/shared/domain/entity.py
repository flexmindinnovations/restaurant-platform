import uuid
from datetime import UTC, datetime
from dataclasses import dataclass, field


@dataclass
class Entity:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class AggregateRoot(Entity):
    _domain_events: list["DomainEvent"] = field(default_factory=list, init=False, repr=False)

    def register_event(self, event: "DomainEvent") -> None:
        self._domain_events.append(event)

    def collect_events(self) -> list["DomainEvent"]:
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events


@dataclass(frozen=True)
class DomainEvent:
    event_id: uuid.UUID = field(default_factory=uuid.uuid4)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))
