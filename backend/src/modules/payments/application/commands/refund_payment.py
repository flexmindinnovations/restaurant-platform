import uuid
from dataclasses import dataclass
from decimal import Decimal

from modules.payments.application.ports.payment_gateway import PaymentGateway
from modules.payments.application.ports.payment_repository import PaymentRepository
from shared.application.ports.unit_of_work import AbstractUnitOfWork
from shared.domain.exceptions import ValidationException


@dataclass(frozen=True)
class RefundPaymentCommand:
    payment_id: uuid.UUID
    amount: Decimal | None = None


class RefundPaymentHandler:
    def __init__(
        self,
        payment_repo: PaymentRepository,
        gateway: PaymentGateway,
        uow: AbstractUnitOfWork,
    ) -> None:
        self._payment_repo = payment_repo
        self._gateway = gateway
        self._uow = uow

    async def handle(self, command: RefundPaymentCommand) -> None:
        payment = await self._payment_repo.get_by_id(command.payment_id)
        if not payment:
            raise ValidationException("Payment not found")

        if not payment.gateway_transaction_id:
            raise ValidationException("Payment is missing gateway transaction ID")

        refund_amount = command.amount if command.amount is not None else payment.amount.amount

        # Call gateway to refund
        response = await self._gateway.refund(payment.gateway_transaction_id, refund_amount)

        async with self._uow:
            payment.refund(refund_amount=refund_amount, response=response)
            await self._payment_repo.update(payment)
            self._uow.register_aggregate(payment)
            await self._uow.commit()


class RefundPaymentByOrderHandler:
    def __init__(
        self,
        payment_repo: PaymentRepository,
        gateway: PaymentGateway,
        uow: AbstractUnitOfWork,
    ) -> None:
        self._payment_repo = payment_repo
        self._gateway = gateway
        self._uow = uow

    async def handle(self, order_id: uuid.UUID) -> None:
        payment = await self._payment_repo.get_by_order_id(order_id)
        if payment:
            handler = RefundPaymentHandler(self._payment_repo, self._gateway, self._uow)
            await handler.handle(RefundPaymentCommand(payment_id=payment.id))
