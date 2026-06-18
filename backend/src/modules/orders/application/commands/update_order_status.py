import uuid
from dataclasses import dataclass

from modules.orders.application.ports.order_repository import OrderRepository
from modules.orders.domain.value_objects.order_status import OrderStatus
from shared.application.ports.unit_of_work import AbstractUnitOfWork
from shared.domain.exceptions import ValidationException


@dataclass(frozen=True)
class UpdateOrderStatusCommand:
    order_id: uuid.UUID
    status: OrderStatus


class UpdateOrderStatusHandler:
    def __init__(self, order_repo: OrderRepository, uow: AbstractUnitOfWork) -> None:
        self._order_repo = order_repo
        self._uow = uow

    async def handle(self, command: UpdateOrderStatusCommand) -> None:
        order = await self._order_repo.get_by_id(command.order_id)
        if not order:
            raise ValidationException("Order not found")

        async with self._uow:
            order.transition_to(command.status)
            await self._order_repo.update(order)
            self._uow.register_aggregate(order)
            await self._uow.commit()
