import uuid
from dataclasses import dataclass

from modules.deliveries.application.ports.partner_repository import PartnerRepository
from modules.deliveries.domain.entities.delivery_partner import DeliveryPartner
from modules.deliveries.domain.value_objects.vehicle_type import VehicleType
from shared.application.ports.unit_of_work import AbstractUnitOfWork


@dataclass(frozen=True)
class RegisterPartnerCommand:
    account_id: uuid.UUID
    name: str
    phone: str
    vehicle_type: VehicleType = VehicleType.MOTORCYCLE


class RegisterPartnerHandler:
    def __init__(
        self,
        partner_repo: PartnerRepository,
        uow: AbstractUnitOfWork,
    ) -> None:
        self._partner_repo = partner_repo
        self._uow = uow

    async def handle(self, command: RegisterPartnerCommand) -> uuid.UUID:
        partner = DeliveryPartner.register(
            account_id=command.account_id,
            name=command.name,
            phone=command.phone,
            vehicle_type=command.vehicle_type,
        )
        async with self._uow:
            await self._partner_repo.add(partner)
            self._uow.register_aggregate(partner)
            await self._uow.commit()
        return partner.id
