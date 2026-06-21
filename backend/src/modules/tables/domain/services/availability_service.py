from __future__ import annotations

from datetime import date, time, timedelta

from modules.tables.domain.entities.reservation import Reservation
from modules.tables.domain.entities.table import Table
from modules.tables.domain.value_objects.table_status import TableStatus


class TimeSlotAvailabilityService:
    def find_available_tables(
        self,
        reservation_date: date,
        start_time: time,
        party_size: int,
        existing_reservations: list[Reservation],
        tables: list[Table],
    ) -> list[Table]:
        available: list[Table] = []
        for table in tables:
            if not table.is_active:
                continue
            if not (table.capacity_min <= party_size <= table.capacity_max):
                continue
            end_time = self.calculate_end_time(start_time, table.turn_time_minutes)
            has_conflict = False
            for res in existing_reservations:
                if res.table_id != table.id:
                    continue
                if res.date != reservation_date:
                    continue
                if res.status.is_terminal:
                    continue
                if self.has_time_conflict(start_time, end_time, res.start_time, res.end_time):
                    has_conflict = True
                    break
            if not has_conflict:
                available.append(table)
        return available

    def calculate_end_time(self, start_time: time, turn_time_minutes: int) -> time:
        start_dt = timedelta(hours=start_time.hour, minutes=start_time.minute)
        end_dt = start_dt + timedelta(minutes=turn_time_minutes)
        total_seconds = int(end_dt.total_seconds())
        hours = (total_seconds // 3600) % 24
        minutes = (total_seconds % 3600) // 60
        return time(hour=hours, minute=minutes)

    def has_time_conflict(self, new_start: time, new_end: time, existing_start: time, existing_end: time) -> bool:
        return new_start < existing_end and new_end > existing_start
