from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db_session, get_settings
from modules.payments.application.commands.add_payment_method import AddPaymentMethodHandler
from modules.payments.application.commands.capture_payment import CapturePaymentHandler
from modules.payments.application.commands.initiate_payment import InitiatePaymentHandler
from modules.payments.application.commands.refund_payment import RefundPaymentHandler
from modules.payments.application.commands.remove_payment_method import RemovePaymentMethodHandler
from modules.payments.application.commands.void_payment import VoidPaymentHandler
from modules.payments.application.ports.payment_gateway import PaymentGateway
from modules.payments.application.ports.payment_method_repository import PaymentMethodRepository
from modules.payments.application.ports.payment_repository import PaymentRepository
from modules.payments.application.queries.get_payment import GetPaymentByOrderHandler
from modules.payments.application.queries.list_payment_methods import ListCustomerPaymentMethodsHandler
from modules.payments.infrastructure.adapters.mock_gateway import MockGateway
from modules.payments.infrastructure.adapters.stripe_gateway import StripeGateway
from modules.payments.infrastructure.repositories.sqlalchemy_payment_repository import (
    SqlAlchemyPaymentMethodRepository,
    SqlAlchemyPaymentRepository,
)
from shared.application.ports.unit_of_work import AbstractUnitOfWork
from shared.infrastructure.event_bus import get_event_bus
from shared.infrastructure.unit_of_work import SqlAlchemyUnitOfWork

# --- Repository & Gateway Providers ---


def _payment_repo(session: AsyncSession = Depends(get_db_session)) -> PaymentRepository:
    return SqlAlchemyPaymentRepository(session)


def _payment_method_repo(session: AsyncSession = Depends(get_db_session)) -> PaymentMethodRepository:
    return SqlAlchemyPaymentMethodRepository(session)


def _payment_gateway(settings=Depends(get_settings)) -> PaymentGateway:
    if settings.stripe_secret_key and settings.stripe_secret_key != "sk_test_51MockKeyChangeInProduction":
        return StripeGateway(settings.stripe_secret_key)
    return MockGateway()


def _uow(session: AsyncSession = Depends(get_db_session)) -> AbstractUnitOfWork:
    return SqlAlchemyUnitOfWork(session, get_event_bus())


# --- Command Handler Providers ---


def get_add_payment_method_handler(
    payment_method_repo: PaymentMethodRepository = Depends(_payment_method_repo),
    uow: AbstractUnitOfWork = Depends(_uow),
) -> AddPaymentMethodHandler:
    return AddPaymentMethodHandler(payment_method_repo, uow)


def get_remove_payment_method_handler(
    payment_method_repo: PaymentMethodRepository = Depends(_payment_method_repo),
    uow: AbstractUnitOfWork = Depends(_uow),
) -> RemovePaymentMethodHandler:
    return RemovePaymentMethodHandler(payment_method_repo, uow)


def get_initiate_payment_handler(
    payment_repo: PaymentRepository = Depends(_payment_repo),
    payment_method_repo: PaymentMethodRepository = Depends(_payment_method_repo),
    gateway: PaymentGateway = Depends(_payment_gateway),
    uow: AbstractUnitOfWork = Depends(_uow),
) -> InitiatePaymentHandler:
    return InitiatePaymentHandler(payment_repo, payment_method_repo, gateway, uow)


def get_capture_payment_handler(
    payment_repo: PaymentRepository = Depends(_payment_repo),
    gateway: PaymentGateway = Depends(_payment_gateway),
    uow: AbstractUnitOfWork = Depends(_uow),
) -> CapturePaymentHandler:
    return CapturePaymentHandler(payment_repo, gateway, uow)


def get_refund_payment_handler(
    payment_repo: PaymentRepository = Depends(_payment_repo),
    gateway: PaymentGateway = Depends(_payment_gateway),
    uow: AbstractUnitOfWork = Depends(_uow),
) -> RefundPaymentHandler:
    return RefundPaymentHandler(payment_repo, gateway, uow)


def get_void_payment_handler(
    payment_repo: PaymentRepository = Depends(_payment_repo),
    gateway: PaymentGateway = Depends(_payment_gateway),
    uow: AbstractUnitOfWork = Depends(_uow),
) -> VoidPaymentHandler:
    return VoidPaymentHandler(payment_repo, gateway, uow)


# --- Query Handler Providers ---


def get_list_payment_methods_handler(
    payment_method_repo: PaymentMethodRepository = Depends(_payment_method_repo),
) -> ListCustomerPaymentMethodsHandler:
    return ListCustomerPaymentMethodsHandler(payment_method_repo)


def get_payment_query_handler(
    payment_repo: PaymentRepository = Depends(_payment_repo),
) -> GetPaymentByOrderHandler:
    return GetPaymentByOrderHandler(payment_repo)
