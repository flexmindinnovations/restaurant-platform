import uuid
from dataclasses import dataclass
from decimal import Decimal

from modules.deliveries.application.ports.delivery_repository import DeliveryRepository
from modules.deliveries.application.ports.partner_repository import PartnerRepository
from shared.application.ports.unit_of_work import AbstractUnitOfWork
from shared.domain.exceptions import ValidationException


@dataclass(frozen=True)
class AssignPartnerCommand:
    delivery_id: uuid.UUID
    initial_radius_km: Decimal = Decimal("5.0")
    max_radius_km: Decimal = Decimal("15.0")
    radius_step_km: Decimal = Decimal("5.0")


class AssignPartnerHandler:
    def __init__(
        self,
        delivery_repo: DeliveryRepository,
        partner_repo: PartnerRepository,
        uow: AbstractUnitOfWork,
    ) -> None:
        self._delivery_repo = delivery_repo
        self._partner_repo = partner_repo
        self._uow = uow

    async def handle(self, command: AssignPartnerCommand) -> uuid.UUID | None:
        async with self._uow:
            delivery = await self._delivery_repo.get_by_id(command.delivery_id)
            if not delivery:
                raise ValidationException(f"Delivery {command.delivery_id} not found")

            origin = delivery.pickup_location or delivery.current_location
            if not origin:
                delivery.fail_assignment()
                await self._delivery_repo.update(delivery)
                self._uow.register_aggregate(delivery)
                await self._uow.commit()
                return None

            radius = command.initial_radius_km
            partner = None

            while radius <= command.max_radius_km:
                partners = await self._partner_repo.find_nearest_available(
                    location=origin,
                    radius_km=radius,
                    limit=5
                )
                if partners:
                    partner = partners[0]
                    break
                radius += command.radius_step_km

            if not partner:
                delivery.fail_assignment()
                await self._delivery_repo.update(delivery)
                self._uow.register_aggregate(delivery)
                await self._uow.commit()
                return None

            delivery.assign(partner.id)
            partner.toggle_availability(False)

            await self._delivery_repo.update(delivery)
            await self._partner_repo.update(partner)

            self._uow.register_aggregate(delivery)
            self._uow.register_aggregate(partner)
            await self._uow.commit()

            return partner.id
