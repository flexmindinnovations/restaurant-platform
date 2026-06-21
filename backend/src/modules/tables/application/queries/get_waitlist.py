from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from modules.tables.application.ports.waitlist_repository import WaitlistRepository


@dataclass(frozen=True)
class WaitlistEntryDTO:
    id: uuid.UUID
    restaurant_id: uuid.UUID
    customer_name: str
    customer_phone: str
    customer_id: uuid.UUID | None
    party_size: int
    estimated_wait_minutes: int
    queue_position: int
    status: str
    preferred_section: uuid.UUID | None
    special_requests: str | None
    notified_at: datetime | None
    seated_at: datetime | None
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class GetWaitlistQuery:
    restaurant_id: uuid.UUID
    skip: int = 0
    limit: int = 50


@dataclass(frozen=True)
class GetWaitlistResult:
    items: list[WaitlistEntryDTO]
    total: int


class GetWaitlistHandler:
    def __init__(self, waitlist_repo: WaitlistRepository) -> None:
        self._waitlist_repo = waitlist_repo

    async def handle(self, query: GetWaitlistQuery) -> GetWaitlistResult:
        entries = await self._waitlist_repo.list_active_by_restaurant(
            restaurant_id=query.restaurant_id,
            skip=query.skip,
            limit=query.limit,
        )
        total = await self._waitlist_repo.count_active_by_restaurant(query.restaurant_id)

        dtos = [
            WaitlistEntryDTO(
                id=e.id,
                restaurant_id=e.restaurant_id,
                customer_name=e.customer_name,
                customer_phone=e.customer_phone,
                customer_id=e.customer_id,
                party_size=e.party_size,
                estimated_wait_minutes=e.estimated_wait_minutes,
                queue_position=e.queue_position,
                status=e.status.value,
                preferred_section=e.preferred_section,
                special_requests=e.special_requests,
                notified_at=e.notified_at,
                seated_at=e.seated_at,
                created_at=e.created_at,
                updated_at=e.updated_at,
            )
            for e in entries
        ]

        return GetWaitlistResult(items=dtos, total=total)
