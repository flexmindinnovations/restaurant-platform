import uuid
from datetime import date, time

import pytest

from modules.tables.domain.entities.reservation import Reservation
from modules.tables.domain.entities.section import Section
from modules.tables.domain.entities.table import Table
from modules.tables.domain.entities.waitlist_entry import WaitlistEntry
from modules.tables.domain.value_objects.reservation_source import ReservationSource
from modules.tables.domain.value_objects.reservation_status import ReservationStatus
from modules.tables.domain.value_objects.table_shape import TableShape
from modules.tables.domain.value_objects.table_status import TableStatus
from modules.tables.domain.value_objects.waitlist_status import WaitlistStatus
from shared.domain.exceptions import ValidationException


@pytest.mark.unit
class TestTable:
    def test_create_table(self):
        restaurant_id = uuid.uuid4()
        table = Table.create(
            restaurant_id=restaurant_id,
            number="T1",
            capacity_min=2,
            capacity_max=4,
            shape=TableShape.ROUND,
        )

        assert table.restaurant_id == restaurant_id
        assert table.number == "T1"
        assert table.capacity_min == 2
        assert table.capacity_max == 4
        assert table.shape == TableShape.ROUND
        assert table.status == TableStatus.AVAILABLE
        assert table.is_active is True

    def test_create_table_empty_number_raises(self):
        with pytest.raises(ValidationException, match="Table number cannot be empty"):
            Table.create(restaurant_id=uuid.uuid4(), number="", capacity_min=1, capacity_max=4)

    def test_create_table_number_too_long_raises(self):
        with pytest.raises(ValidationException, match="must not exceed 20 characters"):
            Table.create(restaurant_id=uuid.uuid4(), number="A" * 21, capacity_min=1, capacity_max=4)

    def test_create_table_invalid_capacity_min_raises(self):
        with pytest.raises(ValidationException, match="Minimum capacity must be at least 1"):
            Table.create(restaurant_id=uuid.uuid4(), number="T1", capacity_min=0, capacity_max=4)

    def test_create_table_capacity_max_less_than_min_raises(self):
        with pytest.raises(ValidationException, match="Maximum capacity must be greater than or equal"):
            Table.create(restaurant_id=uuid.uuid4(), number="T1", capacity_min=5, capacity_max=3)

    def test_change_status_emits_event(self):
        table = Table.create(restaurant_id=uuid.uuid4(), number="T1", capacity_min=1, capacity_max=4)
        table.collect_events()

        table.change_status(TableStatus.OCCUPIED)

        assert table.status == TableStatus.OCCUPIED
        events = table.collect_events()
        assert len(events) == 1
        assert events[0].__class__.__name__ == "TableStatusChanged"
        assert events[0].old_status == TableStatus.AVAILABLE
        assert events[0].new_status == TableStatus.OCCUPIED

    def test_change_status_same_is_noop(self):
        table = Table.create(restaurant_id=uuid.uuid4(), number="T1", capacity_min=1, capacity_max=4)
        table.collect_events()

        table.change_status(TableStatus.AVAILABLE)

        assert table.collect_events() == []

    def test_update_details(self):
        table = Table.create(restaurant_id=uuid.uuid4(), number="T1", capacity_min=1, capacity_max=4)

        table.update_details(number="T2", capacity_max=6, shape=TableShape.BOOTH)

        assert table.number == "T2"
        assert table.capacity_max == 6
        assert table.shape == TableShape.BOOTH

    def test_update_details_empty_number_raises(self):
        table = Table.create(restaurant_id=uuid.uuid4(), number="T1", capacity_min=1, capacity_max=4)
        with pytest.raises(ValidationException, match="Table number cannot be empty"):
            table.update_details(number="")

    def test_deactivate_and_activate(self):
        table = Table.create(restaurant_id=uuid.uuid4(), number="T1", capacity_min=1, capacity_max=4)

        table.deactivate()
        assert table.is_active is False

        table.activate()
        assert table.is_active is True

    def test_can_seat(self):
        table = Table.create(restaurant_id=uuid.uuid4(), number="T1", capacity_min=2, capacity_max=4)

        assert table.can_seat(3) is True
        assert table.can_seat(1) is False
        assert table.can_seat(5) is False

    def test_can_seat_inactive_returns_false(self):
        table = Table.create(restaurant_id=uuid.uuid4(), number="T1", capacity_min=1, capacity_max=4)
        table.deactivate()

        assert table.can_seat(2) is False

    def test_can_seat_occupied_returns_false(self):
        table = Table.create(restaurant_id=uuid.uuid4(), number="T1", capacity_min=1, capacity_max=4)
        table.change_status(TableStatus.OCCUPIED)

        assert table.can_seat(2) is False


@pytest.mark.unit
class TestSection:
    def test_create_section(self):
        restaurant_id = uuid.uuid4()
        section = Section.create(restaurant_id=restaurant_id, name="Patio", description="Outdoor seating")

        assert section.restaurant_id == restaurant_id
        assert section.name == "Patio"
        assert section.description == "Outdoor seating"
        assert section.is_active is True

    def test_create_section_empty_name_raises(self):
        with pytest.raises(ValidationException, match="Section name cannot be empty"):
            Section.create(restaurant_id=uuid.uuid4(), name="")

    def test_update_section(self):
        section = Section.create(restaurant_id=uuid.uuid4(), name="Patio")

        section.update_details(name="Terrace", description="Rooftop")

        assert section.name == "Terrace"
        assert section.description == "Rooftop"

    def test_deactivate_and_activate(self):
        section = Section.create(restaurant_id=uuid.uuid4(), name="Bar")

        section.deactivate()
        assert section.is_active is False

        section.activate()
        assert section.is_active is True


@pytest.mark.unit
class TestReservation:
    def _make_reservation(self, **kwargs):
        defaults = {
            "restaurant_id": uuid.uuid4(),
            "customer_name": "John Doe",
            "date": date(2026, 7, 1),
            "start_time": time(18, 0),
            "end_time": time(19, 30),
            "party_size": 4,
        }
        defaults.update(kwargs)
        return Reservation.create(**defaults)

    def test_create_reservation(self):
        restaurant_id = uuid.uuid4()
        reservation = self._make_reservation(restaurant_id=restaurant_id)

        assert reservation.restaurant_id == restaurant_id
        assert reservation.customer_name == "John Doe"
        assert reservation.party_size == 4
        assert reservation.status == ReservationStatus.PENDING
        assert reservation.source == ReservationSource.PLATFORM

        events = reservation.collect_events()
        assert len(events) == 1
        assert events[0].__class__.__name__ == "ReservationCreated"

    def test_create_reservation_empty_name_raises(self):
        with pytest.raises(ValidationException, match="Customer name cannot be empty"):
            self._make_reservation(customer_name="")

    def test_create_reservation_invalid_party_size_raises(self):
        with pytest.raises(ValidationException, match="Party size must be at least 1"):
            self._make_reservation(party_size=0)

    def test_create_reservation_end_before_start_raises(self):
        with pytest.raises(ValidationException, match="End time must be after start time"):
            self._make_reservation(start_time=time(20, 0), end_time=time(18, 0))

    def test_confirm_reservation(self):
        reservation = self._make_reservation()
        reservation.collect_events()

        table_id = uuid.uuid4()
        reservation.confirm(table_id)

        assert reservation.status == ReservationStatus.CONFIRMED
        assert reservation.table_id == table_id
        events = reservation.collect_events()
        assert any(e.__class__.__name__ == "ReservationConfirmed" for e in events)

    def test_seat_reservation(self):
        reservation = self._make_reservation()
        reservation.confirm(uuid.uuid4())
        reservation.collect_events()

        reservation.seat()

        assert reservation.status == ReservationStatus.SEATED
        assert reservation.seated_at is not None
        events = reservation.collect_events()
        assert any(e.__class__.__name__ == "GuestSeated" for e in events)

    def test_complete_reservation(self):
        reservation = self._make_reservation()
        reservation.confirm(uuid.uuid4())
        reservation.seat()
        reservation.collect_events()

        reservation.complete()

        assert reservation.status == ReservationStatus.COMPLETED
        assert reservation.completed_at is not None

    def test_mark_no_show(self):
        reservation = self._make_reservation()
        reservation.confirm(uuid.uuid4())
        reservation.collect_events()

        reservation.mark_no_show()

        assert reservation.status == ReservationStatus.NO_SHOW
        events = reservation.collect_events()
        assert any(e.__class__.__name__ == "GuestNoShow" for e in events)

    def test_cancel_reservation(self):
        reservation = self._make_reservation()
        reservation.collect_events()

        reservation.cancel(reason="Changed plans")

        assert reservation.status == ReservationStatus.CANCELLED
        assert reservation.cancelled_at is not None
        assert reservation.cancellation_reason == "Changed plans"
        events = reservation.collect_events()
        assert any(e.__class__.__name__ == "ReservationCancelled" for e in events)

    def test_cancel_confirmed_reservation(self):
        reservation = self._make_reservation()
        reservation.confirm(uuid.uuid4())
        reservation.collect_events()

        reservation.cancel()

        assert reservation.status == ReservationStatus.CANCELLED

    def test_cancel_seated_reservation_raises(self):
        reservation = self._make_reservation()
        reservation.confirm(uuid.uuid4())
        reservation.seat()

        with pytest.raises(ValidationException, match="Cannot cancel reservation"):
            reservation.cancel()

    def test_cancel_completed_reservation_raises(self):
        reservation = self._make_reservation()
        reservation.confirm(uuid.uuid4())
        reservation.seat()
        reservation.complete()

        with pytest.raises(ValidationException, match="Cannot cancel reservation"):
            reservation.cancel()

    def test_invalid_transition_pending_to_seated_raises(self):
        reservation = self._make_reservation()
        with pytest.raises(ValidationException, match="Cannot transition"):
            reservation.seat()

    def test_invalid_transition_completed_to_confirmed_raises(self):
        reservation = self._make_reservation()
        reservation.confirm(uuid.uuid4())
        reservation.seat()
        reservation.complete()

        with pytest.raises(ValidationException, match="Cannot transition"):
            reservation.confirm(uuid.uuid4())

    def test_full_lifecycle(self):
        reservation = self._make_reservation()
        assert reservation.status == ReservationStatus.PENDING

        table_id = uuid.uuid4()
        reservation.confirm(table_id)
        assert reservation.status == ReservationStatus.CONFIRMED

        reservation.seat()
        assert reservation.status == ReservationStatus.SEATED

        reservation.complete()
        assert reservation.status == ReservationStatus.COMPLETED


@pytest.mark.unit
class TestWaitlistEntry:
    def _make_entry(self, **kwargs):
        defaults = {
            "restaurant_id": uuid.uuid4(),
            "customer_name": "Jane Smith",
            "customer_phone": "+1234567890",
            "party_size": 3,
            "estimated_wait_minutes": 15,
            "queue_position": 1,
        }
        defaults.update(kwargs)
        return WaitlistEntry.create(**defaults)

    def test_create_entry(self):
        restaurant_id = uuid.uuid4()
        entry = self._make_entry(restaurant_id=restaurant_id)

        assert entry.restaurant_id == restaurant_id
        assert entry.customer_name == "Jane Smith"
        assert entry.party_size == 3
        assert entry.status == WaitlistStatus.WAITING

        events = entry.collect_events()
        assert len(events) == 1
        assert events[0].__class__.__name__ == "WaitlistJoined"

    def test_create_entry_empty_name_raises(self):
        with pytest.raises(ValidationException, match="Customer name cannot be empty"):
            self._make_entry(customer_name="")

    def test_create_entry_empty_phone_raises(self):
        with pytest.raises(ValidationException, match="Customer phone cannot be empty"):
            self._make_entry(customer_phone="")

    def test_create_entry_invalid_party_size_raises(self):
        with pytest.raises(ValidationException, match="Party size must be at least 1"):
            self._make_entry(party_size=0)

    def test_notify_entry(self):
        entry = self._make_entry()
        entry.collect_events()

        entry.notify()

        assert entry.status == WaitlistStatus.NOTIFIED
        assert entry.notified_at is not None
        events = entry.collect_events()
        assert any(e.__class__.__name__ == "WaitlistNotified" for e in events)

    def test_notify_non_waiting_raises(self):
        entry = self._make_entry()
        entry.notify()

        with pytest.raises(ValidationException, match="Cannot notify"):
            entry.notify()

    def test_seat_from_waiting(self):
        entry = self._make_entry()
        entry.collect_events()

        entry.seat()

        assert entry.status == WaitlistStatus.SEATED
        assert entry.seated_at is not None

    def test_seat_from_notified(self):
        entry = self._make_entry()
        entry.notify()

        entry.seat()

        assert entry.status == WaitlistStatus.SEATED

    def test_seat_from_seated_raises(self):
        entry = self._make_entry()
        entry.seat()

        with pytest.raises(ValidationException, match="Cannot seat"):
            entry.seat()

    def test_mark_left(self):
        entry = self._make_entry()

        entry.mark_left()

        assert entry.status == WaitlistStatus.LEFT

    def test_mark_left_from_terminal_raises(self):
        entry = self._make_entry()
        entry.seat()

        with pytest.raises(ValidationException, match="Cannot mark as left"):
            entry.mark_left()

    def test_cancel_entry(self):
        entry = self._make_entry()

        entry.cancel()

        assert entry.status == WaitlistStatus.CANCELLED

    def test_cancel_terminal_raises(self):
        entry = self._make_entry()
        entry.seat()

        with pytest.raises(ValidationException, match="Cannot cancel"):
            entry.cancel()


@pytest.mark.unit
class TestReservationStatus:
    def test_terminal_statuses(self):
        assert ReservationStatus.COMPLETED.is_terminal is True
        assert ReservationStatus.NO_SHOW.is_terminal is True
        assert ReservationStatus.CANCELLED.is_terminal is True
        assert ReservationStatus.PENDING.is_terminal is False
        assert ReservationStatus.CONFIRMED.is_terminal is False
        assert ReservationStatus.SEATED.is_terminal is False

    def test_cancellable_statuses(self):
        assert ReservationStatus.PENDING.is_cancellable is True
        assert ReservationStatus.CONFIRMED.is_cancellable is True
        assert ReservationStatus.SEATED.is_cancellable is False
        assert ReservationStatus.COMPLETED.is_cancellable is False


@pytest.mark.unit
class TestTableStatus:
    def test_is_assignable(self):
        assert TableStatus.AVAILABLE.is_assignable is True
        assert TableStatus.RESERVED.is_assignable is True
        assert TableStatus.OCCUPIED.is_assignable is False
        assert TableStatus.CLEANING.is_assignable is False
        assert TableStatus.BLOCKED.is_assignable is False


@pytest.mark.unit
class TestWaitlistStatus:
    def test_terminal_statuses(self):
        assert WaitlistStatus.SEATED.is_terminal is True
        assert WaitlistStatus.LEFT.is_terminal is True
        assert WaitlistStatus.CANCELLED.is_terminal is True
        assert WaitlistStatus.WAITING.is_terminal is False
        assert WaitlistStatus.NOTIFIED.is_terminal is False
