import uuid
from dataclasses import dataclass

from modules.payments.application.ports.payment_gateway import PaymentGateway
from modules.payments.application.ports.payment_repository import PaymentRepository
from modules.payments.domain.value_objects.payment_status import PaymentStatus
from shared.application.ports.unit_of_work import AbstractUnitOfWork
from shared.domain.exceptions import ValidationException


@dataclass(frozen=True)
class CapturePaymentCommand:
    order_id: uuid.UUID


class CapturePaymentHandler:
    def __init__(
        self,
        payment_repo: PaymentRepository,
        gateway: PaymentGateway,
        uow: AbstractUnitOfWork,
    ) -> None:
        self._payment_repo = payment_repo
        self._gateway = gateway
        self._uow = uow

    async def handle(self, command: CapturePaymentCommand) -> None:
        payment = await self._payment_repo.get_by_order_id(command.order_id)
        if not payment:
            raise ValidationException("Payment not found for order")

        if payment.status == PaymentStatus.CAPTURED:
            return

        if payment.status != PaymentStatus.AUTHORIZED:
            raise ValidationException(f"Cannot capture payment in {payment.status} status")

        if not payment.gateway_transaction_id:
            raise ValidationException("Payment is missing gateway transaction ID")

        # Call gateway to capture
        response = await self._gateway.capture(payment.gateway_transaction_id)

        async with self._uow:
            payment.capture(response=response)
            await self._payment_repo.update(payment)
            self._uow.register_aggregate(payment)
            await self._uow.commit()
