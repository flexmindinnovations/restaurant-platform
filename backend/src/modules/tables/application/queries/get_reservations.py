from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import date, datetime, time

from modules.tables.application.ports.reservation_repository import ReservationRepository


@dataclass(frozen=True)
class ReservationDTO:
    id: uuid.UUID
    restaurant_id: uuid.UUID
    table_id: uuid.UUID | None
    customer_id: uuid.UUID | None
    customer_name: str
    customer_phone: str | None
    customer_email: str | None
    date: date
    start_time: time
    end_time: time
    party_size: int
    status: str
    special_requests: str | None
    internal_notes: str | None
    source: str
    seated_at: datetime | None
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class GetReservationsQuery:
    restaurant_id: uuid.UUID
    reservation_date: date | None = None
    skip: int = 0
    limit: int = 50


@dataclass(frozen=True)
class GetReservationsResult:
    items: list[ReservationDTO]
    total: int


class GetReservationsHandler:
    def __init__(self, reservation_repo: ReservationRepository) -> None:
        self._reservation_repo = reservation_repo

    async def handle(self, query: GetReservationsQuery) -> GetReservationsResult:
        reservations = await self._reservation_repo.list_by_restaurant(
            restaurant_id=query.restaurant_id,
            reservation_date=query.reservation_date,
            skip=query.skip,
            limit=query.limit,
        )
        total = await self._reservation_repo.count_by_restaurant(
            restaurant_id=query.restaurant_id,
            reservation_date=query.reservation_date,
        )

        dtos = [
            ReservationDTO(
                id=r.id,
                restaurant_id=r.restaurant_id,
                table_id=r.table_id,
                customer_id=r.customer_id,
                customer_name=r.customer_name,
                customer_phone=r.customer_phone,
                customer_email=r.customer_email,
                date=r.date,
                start_time=r.start_time,
                end_time=r.end_time,
                party_size=r.party_size,
                status=r.status.value,
                special_requests=r.special_requests,
                internal_notes=r.internal_notes,
                source=r.source.value,
                seated_at=r.seated_at,
                created_at=r.created_at,
                updated_at=r.updated_at,
            )
            for r in reservations
        ]

        return GetReservationsResult(items=dtos, total=total)
