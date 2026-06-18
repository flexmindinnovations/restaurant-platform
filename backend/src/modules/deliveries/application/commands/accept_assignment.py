import uuid
from dataclasses import dataclass

from modules.deliveries.application.ports.delivery_repository import DeliveryRepository
from shared.application.ports.unit_of_work import AbstractUnitOfWork
from shared.domain.exceptions import ValidationException


@dataclass(frozen=True)
class AcceptAssignmentCommand:
    delivery_id: uuid.UUID
    partner_id: uuid.UUID


class AcceptAssignmentHandler:
    def __init__(
        self,
        delivery_repo: DeliveryRepository,
        uow: AbstractUnitOfWork,
    ) -> None:
        self._delivery_repo = delivery_repo
        self._uow = uow

    async def handle(self, command: AcceptAssignmentCommand) -> None:
        async with self._uow:
            delivery = await self._delivery_repo.get_by_id(command.delivery_id)
            if not delivery:
                raise ValidationException(f"Delivery {command.delivery_id} not found")
            if delivery.partner_id != command.partner_id:
                raise ValidationException(
                    f"Delivery {command.delivery_id} is not assigned to partner {command.partner_id}"
                )

            delivery.accept()
            await self._delivery_repo.update(delivery)
            self._uow.register_aggregate(delivery)
            await self._uow.commit()
