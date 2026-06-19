from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db_session
from modules.deliveries.application.commands.accept_assignment import AcceptAssignmentHandler
from modules.deliveries.application.commands.assign_partner import AssignPartnerHandler
from modules.deliveries.application.commands.create_delivery import CreateDeliveryHandler
from modules.deliveries.application.commands.register_partner import RegisterPartnerHandler
from modules.deliveries.application.commands.toggle_partner_availability import TogglePartnerAvailabilityHandler
from modules.deliveries.application.commands.toggle_partner_online import TogglePartnerOnlineHandler
from modules.deliveries.application.commands.update_delivery_status import UpdateDeliveryStatusHandler
from modules.deliveries.application.commands.update_partner_location import UpdatePartnerLocationHandler
from modules.deliveries.application.ports.delivery_repository import DeliveryRepository
from modules.deliveries.application.ports.location_cache import LocationCache
from modules.deliveries.application.ports.partner_repository import PartnerRepository
from modules.deliveries.application.queries.get_delivery import (
    GetDeliveryByOrderHandler,
    GetDeliveryHandler,
)
from modules.deliveries.application.queries.get_partner_location import GetPartnerLocationHandler
from modules.deliveries.application.queries.list_partner_deliveries import ListPartnerDeliveriesHandler
from modules.deliveries.infrastructure.repositories.redis_location_cache import RedisLocationCache
from modules.deliveries.infrastructure.repositories.sqlalchemy_delivery_repository import SqlAlchemyDeliveryRepository
from modules.deliveries.infrastructure.repositories.sqlalchemy_partner_repository import SqlAlchemyPartnerRepository
from shared.application.ports.unit_of_work import AbstractUnitOfWork
from shared.infrastructure.event_bus import get_event_bus
from shared.infrastructure.redis import get_redis
from shared.infrastructure.unit_of_work import SqlAlchemyUnitOfWork

# --- Infrastructure Adapters ---


def _delivery_repo(session: AsyncSession = Depends(get_db_session)) -> DeliveryRepository:
    return SqlAlchemyDeliveryRepository(session)


def _partner_repo(session: AsyncSession = Depends(get_db_session)) -> PartnerRepository:
    return SqlAlchemyPartnerRepository(session)


def _location_cache() -> LocationCache:
    return RedisLocationCache(get_redis())


def _uow(session: AsyncSession = Depends(get_db_session)) -> AbstractUnitOfWork:
    return SqlAlchemyUnitOfWork(session, get_event_bus())


# --- Command Handlers ---


def get_create_delivery_handler(
    delivery_repo: DeliveryRepository = Depends(_delivery_repo),
    uow: AbstractUnitOfWork = Depends(_uow),
) -> CreateDeliveryHandler:
    return CreateDeliveryHandler(delivery_repo, uow)


def get_assign_partner_handler(
    delivery_repo: DeliveryRepository = Depends(_delivery_repo),
    partner_repo: PartnerRepository = Depends(_partner_repo),
    uow: AbstractUnitOfWork = Depends(_uow),
) -> AssignPartnerHandler:
    return AssignPartnerHandler(delivery_repo, partner_repo, uow)


def get_accept_assignment_handler(
    delivery_repo: DeliveryRepository = Depends(_delivery_repo),
    uow: AbstractUnitOfWork = Depends(_uow),
) -> AcceptAssignmentHandler:
    return AcceptAssignmentHandler(delivery_repo, uow)


def get_update_delivery_status_handler(
    delivery_repo: DeliveryRepository = Depends(_delivery_repo),
    uow: AbstractUnitOfWork = Depends(_uow),
) -> UpdateDeliveryStatusHandler:
    return UpdateDeliveryStatusHandler(delivery_repo, uow)


def get_update_partner_location_handler(
    delivery_repo: DeliveryRepository = Depends(_delivery_repo),
    location_cache: LocationCache = Depends(_location_cache),
) -> UpdatePartnerLocationHandler:
    return UpdatePartnerLocationHandler(delivery_repo, location_cache)


def get_toggle_partner_availability_handler(
    partner_repo: PartnerRepository = Depends(_partner_repo),
    uow: AbstractUnitOfWork = Depends(_uow),
) -> TogglePartnerAvailabilityHandler:
    return TogglePartnerAvailabilityHandler(partner_repo, uow)


def get_toggle_partner_online_handler(
    partner_repo: PartnerRepository = Depends(_partner_repo),
    uow: AbstractUnitOfWork = Depends(_uow),
) -> TogglePartnerOnlineHandler:
    return TogglePartnerOnlineHandler(partner_repo, uow)


def get_register_partner_handler(
    partner_repo: PartnerRepository = Depends(_partner_repo),
    uow: AbstractUnitOfWork = Depends(_uow),
) -> RegisterPartnerHandler:
    return RegisterPartnerHandler(partner_repo, uow)


# --- Query Handlers ---


def get_delivery_query_handler(
    delivery_repo: DeliveryRepository = Depends(_delivery_repo),
) -> GetDeliveryHandler:
    return GetDeliveryHandler(delivery_repo)


def get_delivery_by_order_query_handler(
    delivery_repo: DeliveryRepository = Depends(_delivery_repo),
) -> GetDeliveryByOrderHandler:
    return GetDeliveryByOrderHandler(delivery_repo)


def get_list_partner_deliveries_handler(
    delivery_repo: DeliveryRepository = Depends(_delivery_repo),
) -> ListPartnerDeliveriesHandler:
    return ListPartnerDeliveriesHandler(delivery_repo)


def get_partner_location_handler(
    partner_repo: PartnerRepository = Depends(_partner_repo),
    location_cache: LocationCache = Depends(_location_cache),
) -> GetPartnerLocationHandler:
    return GetPartnerLocationHandler(partner_repo, location_cache)
