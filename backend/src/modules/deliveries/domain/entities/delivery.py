import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from modules.deliveries.domain.events.delivery_events import (
    DeliveryCompleted,
    DeliveryCreated,
    LocationUpdated,
    PartnerAssigned,
    PickupCompleted,
)
from modules.deliveries.domain.value_objects.delivery_status import DeliveryStatus
from modules.deliveries.domain.value_objects.location import GeoLocation
from shared.domain.entity import AggregateRoot
from shared.domain.exceptions import ValidationException

_VALID_TRANSITIONS: dict[DeliveryStatus, set[DeliveryStatus]] = {
    DeliveryStatus.PENDING_ASSIGNMENT: {DeliveryStatus.ASSIGNED, DeliveryStatus.NO_PARTNER_AVAILABLE},
    DeliveryStatus.ASSIGNED: {DeliveryStatus.PARTNER_EN_ROUTE_TO_PICKUP, DeliveryStatus.REASSIGNED},
    DeliveryStatus.REASSIGNED: {
        DeliveryStatus.ASSIGNED,
        DeliveryStatus.NO_PARTNER_AVAILABLE,
        DeliveryStatus.PENDING_ASSIGNMENT,
    },
    DeliveryStatus.PARTNER_EN_ROUTE_TO_PICKUP: {DeliveryStatus.AT_PICKUP, DeliveryStatus.REASSIGNED},
    DeliveryStatus.AT_PICKUP: {DeliveryStatus.EN_ROUTE_TO_DELIVERY, DeliveryStatus.REASSIGNED},
    DeliveryStatus.EN_ROUTE_TO_DELIVERY: {DeliveryStatus.AT_DELIVERY},
    DeliveryStatus.AT_DELIVERY: {DeliveryStatus.DELIVERED},
    DeliveryStatus.DELIVERED: set(),
    DeliveryStatus.NO_PARTNER_AVAILABLE: set(),
}


@dataclass
class Delivery(AggregateRoot):
    order_id: uuid.UUID = None  # type: ignore[assignment]
    restaurant_id: uuid.UUID = None  # type: ignore[assignment]
    partner_id: uuid.UUID | None = None
    pickup_address: str = ""
    delivery_address: str = ""
    status: DeliveryStatus = DeliveryStatus.PENDING_ASSIGNMENT
    estimated_pickup_time: datetime | None = None
    actual_pickup_time: datetime | None = None
    estimated_delivery_time: datetime | None = None
    actual_delivery_time: datetime | None = None
    distance_km: Decimal | None = None
    current_location: GeoLocation | None = None
    pickup_location: GeoLocation | None = None
    proof_of_delivery_url: str | None = None

    @classmethod
    def create(
        cls,
        order_id: uuid.UUID,
        restaurant_id: uuid.UUID,
        pickup_address: str,
        delivery_address: str,
        pickup_location: GeoLocation | None = None,
        distance_km: Decimal | None = None,
    ) -> "Delivery":
        delivery_id = uuid.uuid4()
        now = datetime.now(UTC)
        delivery = cls(
            id=delivery_id,
            order_id=order_id,
            restaurant_id=restaurant_id,
            partner_id=None,
            pickup_address=pickup_address,
            delivery_address=delivery_address,
            status=DeliveryStatus.PENDING_ASSIGNMENT,
            distance_km=distance_km,
            pickup_location=pickup_location,
            created_at=now,
            updated_at=now,
        )
        delivery.register_event(
            DeliveryCreated(
                aggregate_id=delivery_id,
                delivery_id=delivery_id,
                order_id=order_id,
                restaurant_id=restaurant_id,
            )
        )
        return delivery

    def transition_to(self, new_status: DeliveryStatus) -> None:
        allowed = _VALID_TRANSITIONS.get(self.status, set())
        if new_status not in allowed:
            raise ValidationException(f"Cannot transition delivery from {self.status} to {new_status}")
        self.status = new_status
        self.updated_at = datetime.now(UTC)

    def assign(self, partner_id: uuid.UUID) -> None:
        self.transition_to(DeliveryStatus.ASSIGNED)
        self.partner_id = partner_id
        # Set estimated times
        now = datetime.now(UTC)
        self.estimated_pickup_time = now + timedelta(minutes=20)
        self.estimated_delivery_time = now + timedelta(minutes=45)
        self.register_event(
            PartnerAssigned(
                aggregate_id=self.id,
                delivery_id=self.id,
                partner_id=partner_id,
            )
        )

    def accept(self) -> None:
        self.transition_to(DeliveryStatus.PARTNER_EN_ROUTE_TO_PICKUP)

    def arrive_at_pickup(self) -> None:
        self.transition_to(DeliveryStatus.AT_PICKUP)

    def pickup(self) -> None:
        self.transition_to(DeliveryStatus.EN_ROUTE_TO_DELIVERY)
        self.actual_pickup_time = datetime.now(UTC)
        self.register_event(
            PickupCompleted(
                aggregate_id=self.id,
                delivery_id=self.id,
            )
        )

    def arrive_at_delivery(self) -> None:
        self.transition_to(DeliveryStatus.AT_DELIVERY)

    def deliver(self, proof_url: str | None = None) -> None:
        self.transition_to(DeliveryStatus.DELIVERED)
        self.actual_delivery_time = datetime.now(UTC)
        self.proof_of_delivery_url = proof_url
        self.register_event(
            DeliveryCompleted(
                aggregate_id=self.id,
                delivery_id=self.id,
                order_id=self.order_id,
            )
        )

    def reassign(self) -> None:
        self.transition_to(DeliveryStatus.REASSIGNED)
        self.partner_id = None

    def fail_assignment(self) -> None:
        self.transition_to(DeliveryStatus.NO_PARTNER_AVAILABLE)

    def update_location(self, location: GeoLocation) -> None:
        self.current_location = location
        self.register_event(
            LocationUpdated(
                aggregate_id=self.id,
                delivery_id=self.id,
                latitude=location.latitude,
                longitude=location.longitude,
            )
        )
