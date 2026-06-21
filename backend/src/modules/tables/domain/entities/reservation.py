import uuid
from dataclasses import dataclass
from datetime import UTC, date, datetime, time

from modules.tables.domain.events.table_events import (
    GuestNoShow,
    GuestSeated,
    ReservationCancelled,
    ReservationConfirmed,
    ReservationCreated,
)
from modules.tables.domain.value_objects.reservation_source import ReservationSource
from modules.tables.domain.value_objects.reservation_status import ReservationStatus
from shared.domain.entity import AggregateRoot
from shared.domain.exceptions import ValidationException


_VALID_TRANSITIONS: dict[ReservationStatus, set[ReservationStatus]] = {
    ReservationStatus.PENDING: {ReservationStatus.CONFIRMED, ReservationStatus.CANCELLED},
    ReservationStatus.CONFIRMED: {ReservationStatus.SEATED, ReservationStatus.NO_SHOW, ReservationStatus.CANCELLED},
    ReservationStatus.SEATED: {ReservationStatus.COMPLETED},
    ReservationStatus.COMPLETED: set(),
    ReservationStatus.NO_SHOW: set(),
    ReservationStatus.CANCELLED: set(),
}


@dataclass
class Reservation(AggregateRoot):
    restaurant_id: uuid.UUID = None  # type: ignore[assignment]
    table_id: uuid.UUID | None = None
    customer_id: uuid.UUID | None = None
    customer_name: str = ""
    customer_phone: str | None = None
    customer_email: str | None = None
    date: date = None  # type: ignore[assignment]
    start_time: time = None  # type: ignore[assignment]
    end_time: time = None  # type: ignore[assignment]
    party_size: int = 1
    status: ReservationStatus = ReservationStatus.PENDING
    special_requests: str | None = None
    internal_notes: str | None = None
    hold_until: datetime | None = None
    seated_at: datetime | None = None
    completed_at: datetime | None = None
    cancelled_at: datetime | None = None
    cancellation_reason: str | None = None
    source: ReservationSource = ReservationSource.PLATFORM

    @classmethod
    def create(
        cls,
        restaurant_id: uuid.UUID,
        customer_name: str,
        date: date,
        start_time: time,
        end_time: time,
        party_size: int,
        source: ReservationSource = ReservationSource.PLATFORM,
        table_id: uuid.UUID | None = None,
        customer_id: uuid.UUID | None = None,
        customer_phone: str | None = None,
        customer_email: str | None = None,
        special_requests: str | None = None,
    ) -> "Reservation":
        if not customer_name:
            raise ValidationException("Customer name cannot be empty")
        if len(customer_name) > 255:
            raise ValidationException("Customer name must not exceed 255 characters")
        if party_size < 1:
            raise ValidationException("Party size must be at least 1")
        if end_time <= start_time:
            raise ValidationException("End time must be after start time")

        reservation_id = uuid.uuid4()
        now = datetime.now(UTC)
        reservation = cls(
            id=reservation_id,
            restaurant_id=restaurant_id,
            table_id=table_id,
            customer_id=customer_id,
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_email=customer_email,
            date=date,
            start_time=start_time,
            end_time=end_time,
            party_size=party_size,
            status=ReservationStatus.PENDING,
            special_requests=special_requests,
            source=source,
            created_at=now,
            updated_at=now,
        )
        reservation.register_event(
            ReservationCreated(
                aggregate_id=reservation_id,
                reservation_id=reservation_id,
                restaurant_id=restaurant_id,
                customer_name=customer_name,
                date=str(date),
                start_time=str(start_time),
                party_size=party_size,
            )
        )
        return reservation

    def _transition_to(self, new_status: ReservationStatus) -> None:
        allowed = _VALID_TRANSITIONS.get(self.status, set())
        if new_status not in allowed:
            raise ValidationException(f"Cannot transition from {self.status} to {new_status}")
        self.status = new_status
        self.updated_at = datetime.now(UTC)

    def confirm(self, table_id: uuid.UUID) -> None:
        self._transition_to(ReservationStatus.CONFIRMED)
        self.table_id = table_id
        self.register_event(
            ReservationConfirmed(
                aggregate_id=self.id,
                reservation_id=self.id,
                restaurant_id=self.restaurant_id,
                table_id=table_id,
            )
        )

    def seat(self, table_id: uuid.UUID | None = None) -> None:
        self._transition_to(ReservationStatus.SEATED)
        now = datetime.now(UTC)
        self.seated_at = now
        if table_id is not None:
            self.table_id = table_id
        self.register_event(
            GuestSeated(
                aggregate_id=self.id,
                reservation_id=self.id,
                restaurant_id=self.restaurant_id,
                table_id=self.table_id,  # type: ignore[arg-type]
                seated_at=now,
            )
        )

    def complete(self) -> None:
        self._transition_to(ReservationStatus.COMPLETED)
        self.completed_at = datetime.now(UTC)

    def mark_no_show(self) -> None:
        self._transition_to(ReservationStatus.NO_SHOW)
        self.register_event(
            GuestNoShow(
                aggregate_id=self.id,
                reservation_id=self.id,
                restaurant_id=self.restaurant_id,
                table_id=self.table_id,
            )
        )

    def cancel(self, reason: str | None = None, cancelled_by: uuid.UUID | None = None) -> None:
        if not self.status.is_cancellable:
            raise ValidationException(f"Cannot cancel reservation in {self.status} status")
        self.status = ReservationStatus.CANCELLED
        self.cancelled_at = datetime.now(UTC)
        self.cancellation_reason = reason
        self.updated_at = datetime.now(UTC)
        self.register_event(
            ReservationCancelled(
                aggregate_id=self.id,
                reservation_id=self.id,
                restaurant_id=self.restaurant_id,
                reason=reason,
                cancelled_by=cancelled_by,
            )
        )
