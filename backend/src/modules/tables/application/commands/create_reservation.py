from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import date, time

from modules.tables.application.ports.reservation_repository import ReservationRepository
from modules.tables.application.ports.table_repository import TableRepository
from modules.tables.domain.entities.reservation import Reservation
from modules.tables.domain.exceptions import ReservationConflictError, TableNotFoundError
from modules.tables.domain.services.availability_service import TimeSlotAvailabilityService
from modules.tables.domain.value_objects.reservation_source import ReservationSource
from shared.application.ports.unit_of_work import AbstractUnitOfWork


@dataclass(frozen=True)
class CreateReservationCommand:
    restaurant_id: uuid.UUID
    customer_name: str
    date: date
    start_time: time
    party_size: int
    table_id: uuid.UUID | None = None
    customer_id: uuid.UUID | None = None
    customer_phone: str | None = None
    customer_email: str | None = None
    special_requests: str | None = None
    source: ReservationSource = ReservationSource.PLATFORM


class CreateReservationHandler:
    def __init__(
        self,
        reservation_repo: ReservationRepository,
        table_repo: TableRepository,
        availability_service: TimeSlotAvailabilityService,
        uow: AbstractUnitOfWork,
    ) -> None:
        self._reservation_repo = reservation_repo
        self._table_repo = table_repo
        self._availability_service = availability_service
        self._uow = uow

    async def handle(self, command: CreateReservationCommand) -> uuid.UUID:
        async with self._uow:
            if command.table_id:
                table = await self._table_repo.get_by_id(command.table_id)
                if not table:
                    raise TableNotFoundError(str(command.table_id))

                end_time = self._availability_service.calculate_end_time(
                    command.start_time, table.turn_time_minutes
                )

                existing = await self._reservation_repo.list_by_table(command.table_id, command.date)
                for res in existing:
                    if res.status.is_terminal:
                        continue
                    if self._availability_service.has_time_conflict(
                        command.start_time, end_time, res.start_time, res.end_time
                    ):
                        raise ReservationConflictError(
                            str(command.table_id), str(command.date), str(command.start_time)
                        )
            else:
                tables = await self._table_repo.list_by_restaurant(
                    command.restaurant_id, active_only=True
                )
                existing = await self._reservation_repo.list_by_restaurant(
                    command.restaurant_id, reservation_date=command.date
                )
                available = self._availability_service.find_available_tables(
                    command.date, command.start_time, command.party_size, existing, tables
                )
                if not available:
                    raise ReservationConflictError("none", str(command.date), str(command.start_time))
                table = available[0]
                end_time = self._availability_service.calculate_end_time(
                    command.start_time, table.turn_time_minutes
                )

            reservation = Reservation.create(
                restaurant_id=command.restaurant_id,
                customer_name=command.customer_name,
                date=command.date,
                start_time=command.start_time,
                end_time=end_time,
                party_size=command.party_size,
                source=command.source,
                table_id=table.id,
                customer_id=command.customer_id,
                customer_phone=command.customer_phone,
                customer_email=command.customer_email,
                special_requests=command.special_requests,
            )
            await self._reservation_repo.add(reservation)
            self._uow.register_aggregate(reservation)
            await self._uow.commit()

        return reservation.id
