import uuid
from dataclasses import dataclass

from modules.orders.application.ports.order_repository import OrderRepository
from shared.application.ports.unit_of_work import AbstractUnitOfWork
from shared.domain.exceptions import ValidationException


@dataclass(frozen=True)
class CancelOrderCommand:
    order_id: uuid.UUID
    reason: str
    user_id: uuid.UUID
    user_roles: list[str]


class CancelOrderHandler:
    def __init__(self, order_repo: OrderRepository, uow: AbstractUnitOfWork) -> None:
        self._order_repo = order_repo
        self._uow = uow

    async def handle(self, command: CancelOrderCommand) -> None:
        order = await self._order_repo.get_by_id(command.order_id)
        if not order:
            raise ValidationException("Order not found")

        # Check authorization
        is_customer = command.user_id == order.customer_id
        is_admin_or_owner = any(role in command.user_roles for role in ["SUPER_ADMIN", "RESTAURANT_OWNER"])

        if not is_customer and not is_admin_or_owner:
            raise ValidationException("Not authorized to cancel this order")

        # Customers can only cancel pending orders
        if is_customer and not is_admin_or_owner and order.status != "PENDING":
            raise ValidationException("Customer can only cancel orders in PENDING status")

        async with self._uow:
            order.cancel(command.reason)
            await self._order_repo.update(order)
            self._uow.register_aggregate(order)
            await self._uow.commit()
