import uuid
from dataclasses import dataclass

from modules.payments.application.ports.payment_method_repository import PaymentMethodRepository
from shared.application.ports.unit_of_work import AbstractUnitOfWork
from shared.domain.exceptions import ValidationException


@dataclass(frozen=True)
class RemovePaymentMethodCommand:
    customer_id: uuid.UUID
    payment_method_id: uuid.UUID


class RemovePaymentMethodHandler:
    def __init__(
        self,
        payment_method_repo: PaymentMethodRepository,
        uow: AbstractUnitOfWork,
    ) -> None:
        self._payment_method_repo = payment_method_repo
        self._uow = uow

    async def handle(self, command: RemovePaymentMethodCommand) -> None:
        method = await self._payment_method_repo.get_by_id(command.payment_method_id)
        if not method or method.customer_id != command.customer_id:
            raise ValidationException("Payment method not found")

        async with self._uow:
            await self._payment_method_repo.delete(command.payment_method_id)
            await self._uow.commit()
