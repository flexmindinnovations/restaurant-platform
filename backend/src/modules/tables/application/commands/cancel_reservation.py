from __future__ import annotations

import uuid
from dataclasses import dataclass

from modules.tables.application.ports.reservation_repository import ReservationRepository
from modules.tables.domain.exceptions import ReservationNotFoundError
from shared.application.ports.unit_of_work import AbstractUnitOfWork


@dataclass(frozen=True)
class CancelReservationCommand:
    reservation_id: uuid.UUID
    reason: str | None = None
    cancelled_by: uuid.UUID | None = None


class CancelReservationHandler:
    def __init__(self, reservation_repo: ReservationRepository, uow: AbstractUnitOfWork) -> None:
        self._reservation_repo = reservation_repo
        self._uow = uow

    async def handle(self, command: CancelReservationCommand) -> None:
        async with self._uow:
            reservation = await self._reservation_repo.get_by_id(command.reservation_id)
            if not reservation:
                raise ReservationNotFoundError(str(command.reservation_id))

            reservation.cancel(reason=command.reason, cancelled_by=command.cancelled_by)
            await self._reservation_repo.update(reservation)
            self._uow.register_aggregate(reservation)
            await self._uow.commit()
