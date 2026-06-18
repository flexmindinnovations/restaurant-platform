from decimal import Decimal
from typing import Any

from sqlalchemy import text

from modules.deliveries.application.commands.assign_partner import AssignPartnerCommand, AssignPartnerHandler
from modules.deliveries.application.commands.create_delivery import CreateDeliveryCommand, CreateDeliveryHandler
from modules.deliveries.domain.value_objects.location import GeoLocation
from modules.deliveries.infrastructure.repositories.sqlalchemy_delivery_repository import SqlAlchemyDeliveryRepository
from modules.deliveries.infrastructure.repositories.sqlalchemy_partner_repository import SqlAlchemyPartnerRepository
from shared.infrastructure.database import get_session_factory
from shared.infrastructure.event_bus import InMemoryEventBus, get_event_bus
from shared.infrastructure.unit_of_work import SqlAlchemyUnitOfWork

_ORDER_DELIVERY_QUERY = text("""
    SELECT
        o.restaurant_id,
        o.delivery_address_street,
        o.delivery_address_city,
        o.delivery_address_state,
        o.delivery_address_postal_code,
        o.delivery_address_country,
        r.address_street,
        r.address_city,
        r.address_state,
        r.address_postal_code,
        r.address_country,
        r.address_latitude,
        r.address_longitude
    FROM orders.orders o
    JOIN restaurants.restaurants r ON o.restaurant_id = r.id
    WHERE o.id = :order_id
""")


def _format_address(street: str, city: str, state: str, postal: str, country: str) -> str:
    return f"{street}, {city}, {state} {postal}, {country}"


async def handle_order_confirmed(event: Any) -> None:
    async with get_session_factory()() as session:
        result = await session.execute(_ORDER_DELIVERY_QUERY, {"order_id": event.aggregate_id})
        row = result.first()
        if not row:
            return

        pickup_loc = None
        if row[11] is not None and row[12] is not None:
            pickup_loc = GeoLocation(latitude=Decimal(str(row[11])), longitude=Decimal(str(row[12])))

        delivery_repo = SqlAlchemyDeliveryRepository(session)
        partner_repo = SqlAlchemyPartnerRepository(session)
        uow = SqlAlchemyUnitOfWork(session, get_event_bus())

        create_cmd = CreateDeliveryCommand(
            order_id=event.aggregate_id,
            restaurant_id=row[0],
            pickup_address=_format_address(row[6], row[7], row[8], row[9], row[10]),
            delivery_address=_format_address(row[1], row[2], row[3], row[4], row[5]),
            pickup_location=pickup_loc,
        )
        delivery_id = await CreateDeliveryHandler(delivery_repo, uow).handle(create_cmd)

        await AssignPartnerHandler(delivery_repo, partner_repo, uow).handle(
            AssignPartnerCommand(delivery_id=delivery_id)
        )


def register_event_handlers(event_bus: InMemoryEventBus) -> None:
    event_bus.subscribe_by_name("OrderConfirmed", handle_order_confirmed)
