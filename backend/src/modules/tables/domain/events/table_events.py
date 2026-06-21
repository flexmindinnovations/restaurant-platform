import uuid
from dataclasses import dataclass, field
from datetime import datetime

from modules.tables.domain.value_objects.table_status import TableStatus
from shared.domain.events import DomainEvent


@dataclass(frozen=True)
class TableStatusChanged(DomainEvent):
    table_id: uuid.UUID = field(default_factory=uuid.uuid4)
    restaurant_id: uuid.UUID = field(default_factory=uuid.uuid4)
    old_status: TableStatus = TableStatus.AVAILABLE
    new_status: TableStatus = TableStatus.AVAILABLE
    changed_by: uuid.UUID | None = None


@dataclass(frozen=True)
class ReservationCreated(DomainEvent):
    reservation_id: uuid.UUID = field(default_factory=uuid.uuid4)
    restaurant_id: uuid.UUID = field(default_factory=uuid.uuid4)
    customer_name: str = ""
    date: str = ""
    start_time: str = ""
    party_size: int = 0


@dataclass(frozen=True)
class ReservationConfirmed(DomainEvent):
    reservation_id: uuid.UUID = field(default_factory=uuid.uuid4)
    restaurant_id: uuid.UUID = field(default_factory=uuid.uuid4)
    table_id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass(frozen=True)
class ReservationCancelled(DomainEvent):
    reservation_id: uuid.UUID = field(default_factory=uuid.uuid4)
    restaurant_id: uuid.UUID = field(default_factory=uuid.uuid4)
    reason: str | None = None
    cancelled_by: uuid.UUID | None = None


@dataclass(frozen=True)
class GuestSeated(DomainEvent):
    reservation_id: uuid.UUID = field(default_factory=uuid.uuid4)
    restaurant_id: uuid.UUID = field(default_factory=uuid.uuid4)
    table_id: uuid.UUID = field(default_factory=uuid.uuid4)
    seated_at: datetime | None = None


@dataclass(frozen=True)
class GuestNoShow(DomainEvent):
    reservation_id: uuid.UUID = field(default_factory=uuid.uuid4)
    restaurant_id: uuid.UUID = field(default_factory=uuid.uuid4)
    table_id: uuid.UUID | None = None


@dataclass(frozen=True)
class WaitlistJoined(DomainEvent):
    waitlist_id: uuid.UUID = field(default_factory=uuid.uuid4)
    restaurant_id: uuid.UUID = field(default_factory=uuid.uuid4)
    party_size: int = 0
    estimated_wait_minutes: int = 0


@dataclass(frozen=True)
class WaitlistNotified(DomainEvent):
    waitlist_id: uuid.UUID = field(default_factory=uuid.uuid4)
    restaurant_id: uuid.UUID = field(default_factory=uuid.uuid4)
    customer_phone: str = ""
