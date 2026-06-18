import uuid
from dataclasses import dataclass

from modules.deliveries.application.ports.partner_repository import PartnerRepository
from shared.application.ports.unit_of_work import AbstractUnitOfWork
from shared.domain.exceptions import ValidationException


@dataclass(frozen=True)
class TogglePartnerOnlineCommand:
    partner_id: uuid.UUID
    is_online: bool


class TogglePartnerOnlineHandler:
    def __init__(
        self,
        partner_repo: PartnerRepository,
        uow: AbstractUnitOfWork,
    ) -> None:
        self._partner_repo = partner_repo
        self._uow = uow

    async def handle(self, command: TogglePartnerOnlineCommand) -> None:
        async with self._uow:
            partner = await self._partner_repo.get_by_id(command.partner_id)
            if not partner:
                raise ValidationException(f"Partner {command.partner_id} not found")

            partner.toggle_online(command.is_online)
            await self._partner_repo.update(partner)
            self._uow.register_aggregate(partner)
            await self._uow.commit()
