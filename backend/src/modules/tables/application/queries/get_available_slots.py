from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import date, time

from modules.tables.application.ports.reservation_repository import ReservationRepository
from modules.tables.application.ports.table_repository import TableRepository
from modules.tables.domain.services.availability_service import TimeSlotAvailabilityService


@dataclass(frozen=True)
class TimeSlotDTO:
    start_time: time
    available_tables: int


@dataclass(frozen=True)
class GetAvailableSlotsQuery:
    restaurant_id: uuid.UUID
    date: date
    party_size: int
    slot_interval_minutes: int = 30
    start_hour: int = 11
    end_hour: int = 22


class GetAvailableSlotsHandler:
    def __init__(
        self,
        table_repo: TableRepository,
        reservation_repo: ReservationRepository,
        availability_service: TimeSlotAvailabilityService,
    ) -> None:
        self._table_repo = table_repo
        self._reservation_repo = reservation_repo
        self._availability_service = availability_service

    async def handle(self, query: GetAvailableSlotsQuery) -> list[TimeSlotDTO]:
        tables = await self._table_repo.list_by_restaurant(query.restaurant_id, active_only=True)
        reservations = await self._reservation_repo.list_by_restaurant(
            query.restaurant_id, reservation_date=query.date
        )

        slots: list[TimeSlotDTO] = []
        current_hour = query.start_hour
        current_minute = 0

        while current_hour < query.end_hour:
            slot_time = time(hour=current_hour, minute=current_minute)
            available = self._availability_service.find_available_tables(
                query.date, slot_time, query.party_size, reservations, tables
            )
            if available:
                slots.append(TimeSlotDTO(start_time=slot_time, available_tables=len(available)))

            current_minute += query.slot_interval_minutes
            if current_minute >= 60:
                current_hour += current_minute // 60
                current_minute = current_minute % 60

        return slots
