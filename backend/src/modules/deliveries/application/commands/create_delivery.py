import uuid
from dataclasses import dataclass
from decimal import Decimal

from modules.deliveries.application.ports.delivery_repository import DeliveryRepository
from modules.deliveries.domain.entities.delivery import Delivery
from shared.application.ports.unit_of_work import AbstractUnitOfWork


@dataclass(frozen=True)
class CreateDeliveryCommand:
    order_id: uuid.UUID
    restaurant_id: uuid.UUID
    pickup_address: str
    delivery_address: str
    distance_km: Decimal | None = None


class CreateDeliveryHandler:
    def __init__(
        self,
        delivery_repo: DeliveryRepository,
        uow: AbstractUnitOfWork,
    ) -> None:
        self._delivery_repo = delivery_repo
        self._uow = uow

    async def handle(self, command: CreateDeliveryCommand) -> uuid.UUID:
        delivery = Delivery.create(
            order_id=command.order_id,
            restaurant_id=command.restaurant_id,
            pickup_address=command.pickup_address,
            delivery_address=command.delivery_address,
            distance_km=command.distance_km,
        )
        async with self._uow:
            await self._delivery_repo.add(delivery)
            self._uow.register_aggregate(delivery)
            await self._uow.commit()
        return delivery.id
