import uuid
from dataclasses import dataclass

from modules.payments.application.ports.payment_gateway import PaymentGateway
from modules.payments.application.ports.payment_repository import PaymentRepository
from modules.payments.domain.value_objects.payment_status import PaymentStatus
from shared.application.ports.unit_of_work import AbstractUnitOfWork
from shared.domain.exceptions import ValidationException


@dataclass(frozen=True)
class VoidPaymentCommand:
    order_id: uuid.UUID


class VoidPaymentHandler:
    def __init__(
        self,
        payment_repo: PaymentRepository,
        gateway: PaymentGateway,
        uow: AbstractUnitOfWork,
    ) -> None:
        self._payment_repo = payment_repo
        self._gateway = gateway
        self._uow = uow

    async def handle(self, command: VoidPaymentCommand) -> None:
        payment = await self._payment_repo.get_by_order_id(command.order_id)
        if not payment:
            return  # No payment initiated, nothing to void

        if payment.status != PaymentStatus.AUTHORIZED:
            return  # Can only void authorized payments

        if not payment.gateway_transaction_id:
            raise ValidationException("Payment is missing gateway transaction ID")

        # Call gateway to void
        response = await self._gateway.void(payment.gateway_transaction_id)

        async with self._uow:
            payment.void(response=response)
            await self._payment_repo.update(payment)
            self._uow.register_aggregate(payment)
            await self._uow.commit()
