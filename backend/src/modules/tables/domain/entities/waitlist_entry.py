import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from modules.tables.domain.events.table_events import WaitlistJoined, WaitlistNotified
from modules.tables.domain.value_objects.waitlist_status import WaitlistStatus
from shared.domain.entity import AggregateRoot
from shared.domain.exceptions import ValidationException


@dataclass
class WaitlistEntry(AggregateRoot):
    restaurant_id: uuid.UUID = None  # type: ignore[assignment]
    customer_name: str = ""
    customer_phone: str = ""
    customer_id: uuid.UUID | None = None
    party_size: int = 1
    estimated_wait_minutes: int = 0
    queue_position: int = 0
    status: WaitlistStatus = WaitlistStatus.WAITING
    preferred_section: uuid.UUID | None = None
    special_requests: str | None = None
    notified_at: datetime | None = None
    seated_at: datetime | None = None

    @classmethod
    def create(
        cls,
        restaurant_id: uuid.UUID,
        customer_name: str,
        customer_phone: str,
        party_size: int,
        estimated_wait_minutes: int,
        queue_position: int,
        customer_id: uuid.UUID | None = None,
        preferred_section: uuid.UUID | None = None,
        special_requests: str | None = None,
    ) -> "WaitlistEntry":
        if not customer_name:
            raise ValidationException("Customer name cannot be empty")
        if len(customer_name) > 255:
            raise ValidationException("Customer name must not exceed 255 characters")
        if not customer_phone:
            raise ValidationException("Customer phone cannot be empty")
        if party_size < 1:
            raise ValidationException("Party size must be at least 1")

        entry_id = uuid.uuid4()
        now = datetime.now(UTC)
        entry = cls(
            id=entry_id,
            restaurant_id=restaurant_id,
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_id=customer_id,
            party_size=party_size,
            estimated_wait_minutes=estimated_wait_minutes,
            queue_position=queue_position,
            status=WaitlistStatus.WAITING,
            preferred_section=preferred_section,
            special_requests=special_requests,
            created_at=now,
            updated_at=now,
        )
        entry.register_event(
            WaitlistJoined(
                aggregate_id=entry_id,
                waitlist_id=entry_id,
                restaurant_id=restaurant_id,
                party_size=party_size,
                estimated_wait_minutes=estimated_wait_minutes,
            )
        )
        return entry

    def notify(self) -> None:
        if self.status != WaitlistStatus.WAITING:
            raise ValidationException(f"Cannot notify waitlist entry in {self.status} status")
        self.status = WaitlistStatus.NOTIFIED
        self.notified_at = datetime.now(UTC)
        self.updated_at = datetime.now(UTC)
        self.register_event(
            WaitlistNotified(
                aggregate_id=self.id,
                waitlist_id=self.id,
                restaurant_id=self.restaurant_id,
                customer_phone=self.customer_phone,
            )
        )

    def seat(self) -> None:
        if self.status not in {WaitlistStatus.WAITING, WaitlistStatus.NOTIFIED}:
            raise ValidationException(f"Cannot seat waitlist entry in {self.status} status")
        self.status = WaitlistStatus.SEATED
        self.seated_at = datetime.now(UTC)
        self.updated_at = datetime.now(UTC)

    def mark_left(self) -> None:
        if self.status.is_terminal:
            raise ValidationException(f"Cannot mark as left: entry is already in {self.status} status")
        self.status = WaitlistStatus.LEFT
        self.updated_at = datetime.now(UTC)

    def cancel(self) -> None:
        if self.status.is_terminal:
            raise ValidationException(f"Cannot cancel waitlist entry in {self.status} status")
        self.status = WaitlistStatus.CANCELLED
        self.updated_at = datetime.now(UTC)
