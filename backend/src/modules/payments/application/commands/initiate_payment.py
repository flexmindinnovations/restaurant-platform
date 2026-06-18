import uuid
from dataclasses import dataclass

from modules.payments.application.ports.payment_gateway import PaymentGateway
from modules.payments.application.ports.payment_method_repository import PaymentMethodRepository
from modules.payments.application.ports.payment_repository import PaymentRepository
from modules.payments.domain.entities.payment import Payment
from shared.application.ports.unit_of_work import AbstractUnitOfWork
from shared.domain.exceptions import ValidationException
from shared.domain.value_objects import Money


@dataclass(frozen=True)
class InitiatePaymentCommand:
    order_id: uuid.UUID
    customer_id: uuid.UUID
    restaurant_id: uuid.UUID
    amount: Money
    payment_method_id: uuid.UUID | None = None


class InitiatePaymentHandler:
    def __init__(
        self,
        payment_repo: PaymentRepository,
        payment_method_repo: PaymentMethodRepository,
        gateway: PaymentGateway,
        uow: AbstractUnitOfWork,
    ) -> None:
        self._payment_repo = payment_repo
        self._payment_method_repo = payment_method_repo
        self._gateway = gateway
        self._uow = uow

    async def _save_payment(self, payment: Payment) -> None:
        async with self._uow:
            await self._payment_repo.update(payment)
            self._uow.register_aggregate(payment)
            await self._uow.commit()

    async def handle(self, command: InitiatePaymentCommand) -> uuid.UUID:
        # 1. Resolve payment method and token
        payment_method = None
        if command.payment_method_id:
            payment_method = await self._payment_method_repo.get_by_id(command.payment_method_id)
        else:
            methods = await self._payment_method_repo.list_by_customer_id(command.customer_id)
            if methods:
                payment_method = next((m for m in methods if m.is_default), methods[0])

        if not payment_method:
            raise ValidationException("No payment method found for customer")

        # 2. Create Payment in PENDING state
        payment = Payment.initiate(
            order_id=command.order_id,
            customer_id=command.customer_id,
            restaurant_id=command.restaurant_id,
            amount=command.amount,
            payment_method_type=payment_method.type,
            payment_method_id=payment_method.id,
        )

        async with self._uow:
            await self._payment_repo.add(payment)
            self._uow.register_aggregate(payment)
            await self._uow.commit()

        # 3. Call gateway to authorize
        try:
            tx_id, response = await self._gateway.authorize(
                amount=command.amount.amount,
                currency=command.amount.currency,
                payment_method_token=payment_method.token,
                customer_id=command.customer_id,
            )
            payment.authorize(gateway_transaction_id=tx_id, response=response)
        except Exception as e:
            reason = str(e)
            payment.fail(reason=reason, response={"error": reason})
            await self._save_payment(payment)
            raise ValidationException(f"Payment authorization failed: {reason}") from e

        await self._save_payment(payment)

        return payment.id
