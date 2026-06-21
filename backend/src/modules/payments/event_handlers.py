from typing import Any

from app.config import get_settings
from modules.payments.application.commands.capture_payment import CapturePaymentCommand, CapturePaymentHandler
from modules.payments.application.commands.initiate_payment import InitiatePaymentCommand, InitiatePaymentHandler
from modules.payments.application.commands.refund_payment import RefundPaymentCommand, RefundPaymentHandler
from modules.payments.application.commands.void_payment import VoidPaymentCommand, VoidPaymentHandler
from modules.payments.domain.value_objects.payment_status import PaymentStatus
from modules.payments.infrastructure.adapters.mock_gateway import MockGateway
from modules.payments.infrastructure.adapters.stripe_gateway import StripeGateway
from modules.payments.infrastructure.repositories.sqlalchemy_payment_repository import (
    SqlAlchemyPaymentMethodRepository,
    SqlAlchemyPaymentRepository,
)
from shared.domain.value_objects import Money
from shared.infrastructure.database import get_session_factory
from shared.infrastructure.event_bus import InMemoryEventBus, get_event_bus
from shared.infrastructure.unit_of_work import SqlAlchemyUnitOfWork


def _get_gateway(settings):
    if settings.stripe_secret_key and settings.stripe_secret_key != "sk_test_51MockKeyChangeInProduction":
        return StripeGateway(settings.stripe_secret_key)
    return MockGateway()


async def handle_order_placed(event: Any) -> None:
    settings = get_settings()
    session_factory = get_session_factory()
    async with session_factory() as session:
        payment_repo = SqlAlchemyPaymentRepository(session)
        payment_method_repo = SqlAlchemyPaymentMethodRepository(session)
        gateway = _get_gateway(settings)
        event_bus = get_event_bus()
        uow = SqlAlchemyUnitOfWork(session, event_bus)

        handler = InitiatePaymentHandler(payment_repo, payment_method_repo, gateway, uow)
        command = InitiatePaymentCommand(
            order_id=event.aggregate_id,
            customer_id=event.customer_id,
            restaurant_id=event.restaurant_id,
            amount=Money(event.total_amount, "INR"),
        )
        await handler.handle(command)


async def handle_order_confirmed(event: Any) -> None:
    settings = get_settings()
    session_factory = get_session_factory()
    async with session_factory() as session:
        payment_repo = SqlAlchemyPaymentRepository(session)
        gateway = _get_gateway(settings)
        event_bus = get_event_bus()
        uow = SqlAlchemyUnitOfWork(session, event_bus)

        payment = await payment_repo.get_by_order_id(event.aggregate_id)
        if not payment:
            return

        handler = CapturePaymentHandler(payment_repo, gateway, uow)
        command = CapturePaymentCommand(payment_id=payment.id)
        await handler.handle(command)


async def handle_order_cancelled(event: Any) -> None:
    settings = get_settings()
    session_factory = get_session_factory()
    async with session_factory() as session:
        payment_repo = SqlAlchemyPaymentRepository(session)
        gateway = _get_gateway(settings)
        event_bus = get_event_bus()
        uow = SqlAlchemyUnitOfWork(session, event_bus)

        payment = await payment_repo.get_by_order_id(event.aggregate_id)
        if not payment:
            return

        if payment.status == PaymentStatus.CAPTURED:
            handler = RefundPaymentHandler(payment_repo, gateway, uow)
            command = RefundPaymentCommand(payment_id=payment.id, amount=payment.amount.amount)
            await handler.handle(command)
        elif payment.status in {PaymentStatus.AUTHORIZED, PaymentStatus.PENDING}:
            handler = VoidPaymentHandler(payment_repo, gateway, uow)
            command = VoidPaymentCommand(payment_id=payment.id)
            await handler.handle(command)


def register_event_handlers(event_bus: InMemoryEventBus) -> None:
    event_bus.subscribe_by_name("OrderPlaced", handle_order_placed)
    event_bus.subscribe_by_name("OrderConfirmed", handle_order_confirmed)
    event_bus.subscribe_by_name("OrderCancelled", handle_order_cancelled)
