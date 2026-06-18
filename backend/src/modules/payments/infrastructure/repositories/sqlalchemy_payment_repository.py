import uuid
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.payments.application.ports.payment_method_repository import PaymentMethodRepository
from modules.payments.application.ports.payment_repository import PaymentRepository
from modules.payments.domain.entities.payment import Payment
from modules.payments.domain.entities.payment_method import PaymentMethod
from modules.payments.domain.value_objects.payment_status import PaymentStatus
from modules.payments.infrastructure.models.payment_models import PaymentMethodModel, PaymentModel
from shared.domain.value_objects import Money


class SqlAlchemyPaymentRepository(PaymentRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_entity(self, model: PaymentModel) -> Payment:
        payment = Payment(
            id=model.id,
            order_id=model.order_id,
            customer_id=model.customer_id,
            restaurant_id=model.restaurant_id,
            amount=Money(Decimal(model.amount_cents) / 100, model.currency),
            status=PaymentStatus(model.status),
            payment_method_type=model.payment_method_type,
            payment_method_id=model.payment_method_id,
            gateway_transaction_id=model.gateway_transaction_id,
            gateway_response=model.gateway_response,
            failure_reason=model.failure_reason,
            captured_at=model.captured_at,
            refunded_at=model.refunded_at,
        )
        payment.created_at = model.created_at
        payment.updated_at = model.updated_at
        return payment

    async def add(self, payment: Payment) -> None:
        model = PaymentModel(
            id=payment.id,
            order_id=payment.order_id,
            customer_id=payment.customer_id,
            restaurant_id=payment.restaurant_id,
            amount_cents=int(payment.amount.amount * 100),
            currency=payment.amount.currency,
            status=payment.status,
            payment_method_type=payment.payment_method_type,
            payment_method_id=payment.payment_method_id,
            gateway_transaction_id=payment.gateway_transaction_id,
            gateway_response=payment.gateway_response,
            failure_reason=payment.failure_reason,
            captured_at=payment.captured_at,
            refunded_at=payment.refunded_at,
            created_at=payment.created_at,
            updated_at=payment.updated_at,
        )
        self._session.add(model)

    async def update(self, payment: Payment) -> None:
        result = await self._session.execute(select(PaymentModel).where(PaymentModel.id == payment.id))
        model = result.scalar_one_or_none()
        if model:
            model.status = payment.status
            model.gateway_transaction_id = payment.gateway_transaction_id
            model.gateway_response = payment.gateway_response
            model.failure_reason = payment.failure_reason
            model.captured_at = payment.captured_at
            model.refunded_at = payment.refunded_at
            model.updated_at = payment.updated_at

    async def get_by_id(self, payment_id: uuid.UUID) -> Payment | None:
        result = await self._session.execute(select(PaymentModel).where(PaymentModel.id == payment_id))
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_order_id(self, order_id: uuid.UUID) -> Payment | None:
        result = await self._session.execute(select(PaymentModel).where(PaymentModel.order_id == order_id))
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None


class SqlAlchemyPaymentMethodRepository(PaymentMethodRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_entity(self, model: PaymentMethodModel) -> PaymentMethod:
        method = PaymentMethod(
            id=model.id,
            customer_id=model.customer_id,
            type=model.type,
            last_four=model.last_four,
            brand=model.brand,
            is_default=model.is_default,
            token=model.token,
        )
        method.created_at = model.created_at
        method.updated_at = model.updated_at
        return method

    async def add(self, payment_method: PaymentMethod) -> None:
        result = await self._session.execute(
            select(PaymentMethodModel).where(PaymentMethodModel.id == payment_method.id)
        )
        model = result.scalar_one_or_none()
        if not model:
            model = PaymentMethodModel(
                id=payment_method.id,
                customer_id=payment_method.customer_id,
                type=payment_method.type,
                last_four=payment_method.last_four,
                brand=payment_method.brand,
                is_default=payment_method.is_default,
                token=payment_method.token,
                created_at=payment_method.created_at,
                updated_at=payment_method.updated_at,
            )
            self._session.add(model)
        else:
            model.is_default = payment_method.is_default
            model.updated_at = payment_method.updated_at

    async def delete(self, payment_method_id: uuid.UUID) -> None:
        result = await self._session.execute(
            select(PaymentMethodModel).where(PaymentMethodModel.id == payment_method_id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)

    async def list_by_customer_id(self, customer_id: uuid.UUID) -> list[PaymentMethod]:
        result = await self._session.execute(
            select(PaymentMethodModel).where(PaymentMethodModel.customer_id == customer_id)
        )
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def get_by_id(self, payment_method_id: uuid.UUID) -> PaymentMethod | None:
        result = await self._session.execute(
            select(PaymentMethodModel).where(PaymentMethodModel.id == payment_method_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None
