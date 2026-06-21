import uuid
from datetime import date, time

import pytest

from modules.tables.domain.entities.reservation import Reservation
from modules.tables.domain.entities.table import Table
from modules.tables.domain.services.availability_service import TimeSlotAvailabilityService
from modules.tables.domain.value_objects.table_shape import TableShape


@pytest.mark.unit
class TestTimeSlotAvailabilityService:
    def setup_method(self):
        self.service = TimeSlotAvailabilityService()
        self.restaurant_id = uuid.uuid4()

    def _make_table(self, number: str, capacity_min: int = 1, capacity_max: int = 4, **kwargs) -> Table:
        return Table.create(
            restaurant_id=self.restaurant_id,
            number=number,
            capacity_min=capacity_min,
            capacity_max=capacity_max,
            shape=TableShape.RECTANGULAR,
            **kwargs,
        )

    def _make_reservation(
        self,
        table: Table,
        reservation_date: date,
        start: time,
        end: time,
        party_size: int = 2,
    ) -> Reservation:
        return Reservation.create(
            restaurant_id=self.restaurant_id,
            customer_name="Test Guest",
            date=reservation_date,
            start_time=start,
            end_time=end,
            party_size=party_size,
            table_id=table.id,
        )

    def test_all_tables_available_when_no_reservations(self):
        t1 = self._make_table("T1", capacity_max=4)
        t2 = self._make_table("T2", capacity_max=6)

        result = self.service.find_available_tables(
            reservation_date=date(2026, 7, 1),
            start_time=time(18, 0),
            party_size=2,
            existing_reservations=[],
            tables=[t1, t2],
        )

        assert len(result) == 2

    def test_filters_by_capacity(self):
        t1 = self._make_table("T1", capacity_min=1, capacity_max=2)
        t2 = self._make_table("T2", capacity_min=4, capacity_max=8)

        result = self.service.find_available_tables(
            reservation_date=date(2026, 7, 1),
            start_time=time(18, 0),
            party_size=6,
            existing_reservations=[],
            tables=[t1, t2],
        )

        assert len(result) == 1
        assert result[0].id == t2.id

    def test_filters_inactive_tables(self):
        t1 = self._make_table("T1")
        t2 = self._make_table("T2")
        t2.deactivate()

        result = self.service.find_available_tables(
            reservation_date=date(2026, 7, 1),
            start_time=time(18, 0),
            party_size=2,
            existing_reservations=[],
            tables=[t1, t2],
        )

        assert len(result) == 1
        assert result[0].id == t1.id

    def test_excludes_table_with_conflicting_reservation(self):
        t1 = self._make_table("T1")
        res = self._make_reservation(t1, date(2026, 7, 1), time(18, 0), time(19, 30))

        result = self.service.find_available_tables(
            reservation_date=date(2026, 7, 1),
            start_time=time(18, 30),
            party_size=2,
            existing_reservations=[res],
            tables=[t1],
        )

        assert len(result) == 0

    def test_allows_table_with_non_overlapping_reservation(self):
        t1 = self._make_table("T1")
        res = self._make_reservation(t1, date(2026, 7, 1), time(12, 0), time(13, 30))

        result = self.service.find_available_tables(
            reservation_date=date(2026, 7, 1),
            start_time=time(18, 0),
            party_size=2,
            existing_reservations=[res],
            tables=[t1],
        )

        assert len(result) == 1

    def test_ignores_terminal_reservations(self):
        t1 = self._make_table("T1")
        res = self._make_reservation(t1, date(2026, 7, 1), time(18, 0), time(19, 30))
        res.confirm(t1.id)
        res.seat()
        res.complete()

        result = self.service.find_available_tables(
            reservation_date=date(2026, 7, 1),
            start_time=time(18, 0),
            party_size=2,
            existing_reservations=[res],
            tables=[t1],
        )

        assert len(result) == 1

    def test_ignores_cancelled_reservations(self):
        t1 = self._make_table("T1")
        res = self._make_reservation(t1, date(2026, 7, 1), time(18, 0), time(19, 30))
        res.cancel(reason="no longer needed")

        result = self.service.find_available_tables(
            reservation_date=date(2026, 7, 1),
            start_time=time(18, 0),
            party_size=2,
            existing_reservations=[res],
            tables=[t1],
        )

        assert len(result) == 1

    def test_different_date_no_conflict(self):
        t1 = self._make_table("T1")
        res = self._make_reservation(t1, date(2026, 7, 1), time(18, 0), time(19, 30))

        result = self.service.find_available_tables(
            reservation_date=date(2026, 7, 2),
            start_time=time(18, 0),
            party_size=2,
            existing_reservations=[res],
            tables=[t1],
        )

        assert len(result) == 1

    def test_reservation_on_different_table_no_conflict(self):
        t1 = self._make_table("T1")
        t2 = self._make_table("T2")
        res = self._make_reservation(t2, date(2026, 7, 1), time(18, 0), time(19, 30))

        result = self.service.find_available_tables(
            reservation_date=date(2026, 7, 1),
            start_time=time(18, 0),
            party_size=2,
            existing_reservations=[res],
            tables=[t1],
        )

        assert len(result) == 1

    def test_calculate_end_time(self):
        end = self.service.calculate_end_time(time(18, 0), 90)
        assert end == time(19, 30)

    def test_calculate_end_time_wraps_midnight(self):
        end = self.service.calculate_end_time(time(23, 0), 120)
        assert end == time(1, 0)

    def test_has_time_conflict_overlap(self):
        assert self.service.has_time_conflict(time(18, 0), time(19, 30), time(19, 0), time(20, 30)) is True

    def test_has_time_conflict_no_overlap(self):
        assert self.service.has_time_conflict(time(18, 0), time(19, 30), time(20, 0), time(21, 30)) is False

    def test_has_time_conflict_adjacent_no_overlap(self):
        assert self.service.has_time_conflict(time(18, 0), time(19, 30), time(19, 30), time(21, 0)) is False

    def test_has_time_conflict_contained(self):
        assert self.service.has_time_conflict(time(17, 0), time(21, 0), time(18, 0), time(20, 0)) is True
