from __future__ import annotations

import uuid
from dataclasses import dataclass

from modules.tables.application.ports.waitlist_repository import WaitlistRepository
from modules.tables.domain.entities.waitlist_entry import WaitlistEntry
from shared.application.ports.unit_of_work import AbstractUnitOfWork


@dataclass(frozen=True)
class JoinWaitlistCommand:
    restaurant_id: uuid.UUID
    customer_name: str
    customer_phone: str
    party_size: int
    estimated_wait_minutes: int
    customer_id: uuid.UUID | None = None
    preferred_section: uuid.UUID | None = None
    special_requests: str | None = None


class JoinWaitlistHandler:
    def __init__(self, waitlist_repo: WaitlistRepository, uow: AbstractUnitOfWork) -> None:
        self._waitlist_repo = waitlist_repo
        self._uow = uow

    async def handle(self, command: JoinWaitlistCommand) -> uuid.UUID:
        async with self._uow:
            queue_position = await self._waitlist_repo.get_next_position(command.restaurant_id)

            entry = WaitlistEntry.create(
                restaurant_id=command.restaurant_id,
                customer_name=command.customer_name,
                customer_phone=command.customer_phone,
                party_size=command.party_size,
                estimated_wait_minutes=command.estimated_wait_minutes,
                queue_position=queue_position,
                customer_id=command.customer_id,
                preferred_section=command.preferred_section,
                special_requests=command.special_requests,
            )
            await self._waitlist_repo.add(entry)
            self._uow.register_aggregate(entry)
            await self._uow.commit()

        return entry.id
