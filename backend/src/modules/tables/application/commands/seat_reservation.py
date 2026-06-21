from __future__ import annotations

import uuid
from dataclasses import dataclass

from modules.tables.application.ports.reservation_repository import ReservationRepository
from modules.tables.application.ports.table_repository import TableRepository
from modules.tables.domain.exceptions import ReservationNotFoundError, TableNotFoundError
from modules.tables.domain.value_objects.table_status import TableStatus
from shared.application.ports.unit_of_work import AbstractUnitOfWork


@dataclass(frozen=True)
class SeatReservationCommand:
    reservation_id: uuid.UUID
    table_id: uuid.UUID | None = None


class SeatReservationHandler:
    def __init__(
        self,
        reservation_repo: ReservationRepository,
        table_repo: TableRepository,
        uow: AbstractUnitOfWork,
    ) -> None:
        self._reservation_repo = reservation_repo
        self._table_repo = table_repo
        self._uow = uow

    async def handle(self, command: SeatReservationCommand) -> None:
        async with self._uow:
            reservation = await self._reservation_repo.get_by_id(command.reservation_id)
            if not reservation:
                raise ReservationNotFoundError(str(command.reservation_id))

            target_table_id = command.table_id or reservation.table_id
            if not target_table_id:
                raise TableNotFoundError("None")

            table = await self._table_repo.get_by_id(target_table_id)
            if not table:
                raise TableNotFoundError(str(target_table_id))

            reservation.seat(table_id=command.table_id)
            table.change_status(TableStatus.OCCUPIED)

            await self._reservation_repo.update(reservation)
            await self._table_repo.update(table)
            self._uow.register_aggregate(reservation)
            self._uow.register_aggregate(table)
            await self._uow.commit()
