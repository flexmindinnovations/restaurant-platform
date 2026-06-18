import uuid
from dataclasses import dataclass

from modules.deliveries.application.ports.delivery_repository import DeliveryRepository
from modules.deliveries.domain.value_objects.delivery_status import DeliveryStatus
from shared.application.ports.unit_of_work import AbstractUnitOfWork
from shared.domain.exceptions import ValidationException


@dataclass(frozen=True)
class UpdateDeliveryStatusCommand:
    delivery_id: uuid.UUID
    partner_id: uuid.UUID
    status: DeliveryStatus
    proof_of_delivery_url: str | None = None


class UpdateDeliveryStatusHandler:
    def __init__(
        self,
        delivery_repo: DeliveryRepository,
        uow: AbstractUnitOfWork,
    ) -> None:
        self._delivery_repo = delivery_repo
        self._uow = uow

    async def handle(self, command: UpdateDeliveryStatusCommand) -> None:
        async with self._uow:
            delivery = await self._delivery_repo.get_by_id(command.delivery_id)
            if not delivery:
                raise ValidationException(f"Delivery {command.delivery_id} not found")
            if delivery.partner_id != command.partner_id:
                raise ValidationException(
                    f"Delivery {command.delivery_id} is not assigned to partner {command.partner_id}"
                )

            # Map target state to domain entity methods
            if command.status == DeliveryStatus.PARTNER_EN_ROUTE_TO_PICKUP:
                delivery.accept()
            elif command.status == DeliveryStatus.AT_PICKUP:
                delivery.arrive_at_pickup()
            elif command.status == DeliveryStatus.EN_ROUTE_TO_DELIVERY:
                delivery.pickup()
            elif command.status == DeliveryStatus.AT_DELIVERY:
                delivery.arrive_at_delivery()
            elif command.status == DeliveryStatus.DELIVERED:
                delivery.deliver(command.proof_of_delivery_url)
            elif command.status == DeliveryStatus.REASSIGNED:
                delivery.reassign()
            else:
                raise ValidationException(f"Unsupported manual state transition: {command.status}")

            await self._delivery_repo.update(delivery)
            self._uow.register_aggregate(delivery)
            await self._uow.commit()
