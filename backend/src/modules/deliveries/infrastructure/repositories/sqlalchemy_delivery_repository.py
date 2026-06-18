import uuid
from decimal import Decimal

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from modules.deliveries.application.ports.delivery_repository import DeliveryRepository
from modules.deliveries.domain.entities.delivery import Delivery
from modules.deliveries.domain.value_objects.delivery_status import DeliveryStatus
from modules.deliveries.domain.value_objects.location import GeoLocation
from modules.deliveries.infrastructure.models.delivery_models import DeliveryModel


class SqlAlchemyDeliveryRepository(DeliveryRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _row_to_entity(self, row) -> Delivery:
        model = row[0]
        curr_lon = row[1]
        curr_lat = row[2]
        pick_lon = row[3]
        pick_lat = row[4]

        current_loc = None
        if curr_lon is not None and curr_lat is not None:
            current_loc = GeoLocation(latitude=Decimal(str(curr_lat)), longitude=Decimal(str(curr_lon)))

        pickup_loc = None
        if pick_lon is not None and pick_lat is not None:
            pickup_loc = GeoLocation(latitude=Decimal(str(pick_lat)), longitude=Decimal(str(pick_lon)))

        delivery = Delivery(
            id=model.id,
            order_id=model.order_id,
            restaurant_id=model.restaurant_id,
            partner_id=model.partner_id,
            pickup_address=model.pickup_address,
            delivery_address=model.delivery_address,
            status=DeliveryStatus(model.status),
            estimated_pickup_time=model.estimated_pickup_time,
            actual_pickup_time=model.actual_pickup_time,
            estimated_delivery_time=model.estimated_delivery_time,
            actual_delivery_time=model.actual_delivery_time,
            distance_km=Decimal(str(model.distance_km)) if model.distance_km is not None else None,
            current_location=current_loc,
            pickup_location=pickup_loc,
            proof_of_delivery_url=model.proof_of_delivery_url,
        )
        delivery.created_at = model.created_at
        delivery.updated_at = model.updated_at
        return delivery

    async def add(self, delivery: Delivery) -> None:
        model = DeliveryModel(
            id=delivery.id,
            order_id=delivery.order_id,
            restaurant_id=delivery.restaurant_id,
            partner_id=delivery.partner_id,
            pickup_address=delivery.pickup_address,
            delivery_address=delivery.delivery_address,
            status=delivery.status.value if hasattr(delivery.status, "value") else str(delivery.status),
            estimated_pickup_time=delivery.estimated_pickup_time,
            actual_pickup_time=delivery.actual_pickup_time,
            estimated_delivery_time=delivery.estimated_delivery_time,
            actual_delivery_time=delivery.actual_delivery_time,
            distance_km=float(delivery.distance_km) if delivery.distance_km is not None else None,
            proof_of_delivery_url=delivery.proof_of_delivery_url,
            created_at=delivery.created_at,
            updated_at=delivery.updated_at,
        )
        if delivery.pickup_location:
            loc = delivery.pickup_location
            model.pickup_location = text(
                f"ST_GeogFromText('SRID=4326;POINT({loc.longitude} {loc.latitude})')"
            )
        if delivery.current_location:
            loc = delivery.current_location
            model.current_location = text(
                f"ST_GeogFromText('SRID=4326;POINT({loc.longitude} {loc.latitude})')"
            )

        self._session.add(model)

    async def update(self, delivery: Delivery) -> None:
        result = await self._session.execute(
            select(DeliveryModel).where(DeliveryModel.id == delivery.id)
        )
        model = result.scalar_one_or_none()
        if model:
            model.partner_id = delivery.partner_id
            model.status = delivery.status.value if hasattr(delivery.status, "value") else str(delivery.status)
            model.estimated_pickup_time = delivery.estimated_pickup_time
            model.actual_pickup_time = delivery.actual_pickup_time
            model.estimated_delivery_time = delivery.estimated_delivery_time
            model.actual_delivery_time = delivery.actual_delivery_time
            model.proof_of_delivery_url = delivery.proof_of_delivery_url
            model.updated_at = delivery.updated_at

            if delivery.pickup_location:
                loc = delivery.pickup_location
                model.pickup_location = text(
                    f"ST_GeogFromText('SRID=4326;POINT({loc.longitude} {loc.latitude})')"
                )
            else:
                model.pickup_location = None

            if delivery.current_location:
                loc = delivery.current_location
                model.current_location = text(
                    f"ST_GeogFromText('SRID=4326;POINT({loc.longitude} {loc.latitude})')"
                )
            else:
                model.current_location = None

    async def get_by_id(self, delivery_id: uuid.UUID) -> Delivery | None:
        result = await self._session.execute(
            select(
                DeliveryModel,
                text("ST_X(current_location::geometry)"),
                text("ST_Y(current_location::geometry)"),
                text("ST_X(pickup_location::geometry)"),
                text("ST_Y(pickup_location::geometry)"),
            ).where(DeliveryModel.id == delivery_id)
        )
        row = result.first()
        return self._row_to_entity(row) if row else None

    async def get_by_order_id(self, order_id: uuid.UUID) -> Delivery | None:
        result = await self._session.execute(
            select(
                DeliveryModel,
                text("ST_X(current_location::geometry)"),
                text("ST_Y(current_location::geometry)"),
                text("ST_X(pickup_location::geometry)"),
                text("ST_Y(pickup_location::geometry)"),
            ).where(DeliveryModel.order_id == order_id)
        )
        row = result.first()
        return self._row_to_entity(row) if row else None

    async def get_active_by_partner_id(self, partner_id: uuid.UUID) -> Delivery | None:
        # Active statuses are anything other than DELIVERED or NO_PARTNER_AVAILABLE
        result = await self._session.execute(
            select(
                DeliveryModel,
                text("ST_X(current_location::geometry)"),
                text("ST_Y(current_location::geometry)"),
                text("ST_X(pickup_location::geometry)"),
                text("ST_Y(pickup_location::geometry)"),
            ).where(
                DeliveryModel.partner_id == partner_id,
                DeliveryModel.status.notin_(["DELIVERED", "NO_PARTNER_AVAILABLE"])
            )
        )
        row = result.first()
        return self._row_to_entity(row) if row else None

    async def list_by_partner_id(self, partner_id: uuid.UUID) -> list[Delivery]:
        result = await self._session.execute(
            select(
                DeliveryModel,
                text("ST_X(current_location::geometry)"),
                text("ST_Y(current_location::geometry)"),
                text("ST_X(pickup_location::geometry)"),
                text("ST_Y(pickup_location::geometry)"),
            ).where(DeliveryModel.partner_id == partner_id)
        )
        rows = result.all()
        return [self._row_to_entity(r) for r in rows]
