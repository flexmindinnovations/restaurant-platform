import uuid
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from modules.deliveries.application.ports.delivery_repository import DeliveryRepository
from shared.domain.exceptions import ValidationException


@dataclass
class DeliveryDTO:
    id: uuid.UUID
    order_id: uuid.UUID
    restaurant_id: uuid.UUID
    partner_id: uuid.UUID | None
    pickup_address: str
    delivery_address: str
    status: str
    estimated_pickup_time: datetime | None
    actual_pickup_time: datetime | None
    estimated_delivery_time: datetime | None
    actual_delivery_time: datetime | None
    distance_km: Decimal | None
    current_location_lat: Decimal | None
    current_location_lon: Decimal | None
    pickup_location_lat: Decimal | None
    pickup_location_lon: Decimal | None
    proof_of_delivery_url: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, d) -> "DeliveryDTO":
        return cls(
            id=d.id,
            order_id=d.order_id,
            restaurant_id=d.restaurant_id,
            partner_id=d.partner_id,
            pickup_address=d.pickup_address,
            delivery_address=d.delivery_address,
            status=d.status.value if hasattr(d.status, "value") else str(d.status),
            estimated_pickup_time=d.estimated_pickup_time,
            actual_pickup_time=d.actual_pickup_time,
            estimated_delivery_time=d.estimated_delivery_time,
            actual_delivery_time=d.actual_delivery_time,
            distance_km=d.distance_km,
            current_location_lat=d.current_location.latitude if d.current_location else None,
            current_location_lon=d.current_location.longitude if d.current_location else None,
            pickup_location_lat=d.pickup_location.latitude if getattr(d, "pickup_location", None) else None,
            pickup_location_lon=d.pickup_location.longitude if getattr(d, "pickup_location", None) else None,
            proof_of_delivery_url=d.proof_of_delivery_url,
            created_at=d.created_at,
            updated_at=d.updated_at,
        )


@dataclass(frozen=True)
class GetDeliveryQuery:
    delivery_id: uuid.UUID


class GetDeliveryHandler:
    def __init__(self, delivery_repo: DeliveryRepository) -> None:
        self._delivery_repo = delivery_repo

    async def handle(self, query: GetDeliveryQuery) -> DeliveryDTO:
        d = await self._delivery_repo.get_by_id(query.delivery_id)
        if not d:
            raise ValidationException("Delivery not found")
        return DeliveryDTO.from_entity(d)


@dataclass(frozen=True)
class GetDeliveryByOrderQuery:
    order_id: uuid.UUID


class GetDeliveryByOrderHandler:
    def __init__(self, delivery_repo: DeliveryRepository) -> None:
        self._delivery_repo = delivery_repo

    async def handle(self, query: GetDeliveryByOrderQuery) -> DeliveryDTO:
        d = await self._delivery_repo.get_by_order_id(query.order_id)
        if not d:
            raise ValidationException("Delivery not found for order")
        return DeliveryDTO.from_entity(d)
