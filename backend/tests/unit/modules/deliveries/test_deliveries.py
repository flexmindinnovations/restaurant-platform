import uuid
from decimal import Decimal
import pytest

from modules.deliveries.domain.entities.delivery import Delivery
from modules.deliveries.domain.entities.delivery_partner import DeliveryPartner
from modules.deliveries.domain.value_objects.delivery_status import DeliveryStatus
from modules.deliveries.domain.value_objects.location import GeoLocation
from modules.deliveries.domain.value_objects.vehicle_type import VehicleType
from shared.domain.exceptions import ValidationException


def test_haversine_distance():
    # Space Needle (Seattle) and Pike Place Market
    loc1 = GeoLocation(latitude=Decimal("47.6205"), longitude=Decimal("-122.3493"))
    loc2 = GeoLocation(latitude=Decimal("47.6097"), longitude=Decimal("-122.3422"))

    distance = loc1.distance_to(loc2)
    # The actual distance is ~1.33 km
    assert abs(distance - Decimal("1.33")) < Decimal("0.1")


def test_delivery_state_lifecycle():
    order_id = uuid.uuid4()
    restaurant_id = uuid.uuid4()
    pickup_address = "Space Needle, Seattle"
    delivery_address = "Pike Place, Seattle"
    pickup_loc = GeoLocation(latitude=Decimal("47.6205"), longitude=Decimal("-122.3493"))

    d = Delivery.create(
        order_id=order_id,
        restaurant_id=restaurant_id,
        pickup_address=pickup_address,
        delivery_address=delivery_address,
        pickup_location=pickup_loc,
    )

    assert d.status == DeliveryStatus.PENDING_ASSIGNMENT
    assert d.pickup_location == pickup_loc

    # Assign partner
    partner_id = uuid.uuid4()
    d.assign(partner_id)
    assert d.status == DeliveryStatus.ASSIGNED
    assert d.partner_id == partner_id

    # Accept
    d.accept()
    assert d.status == DeliveryStatus.PARTNER_EN_ROUTE_TO_PICKUP

    # Arrive at pickup
    d.arrive_at_pickup()
    assert d.status == DeliveryStatus.AT_PICKUP

    # Pickup
    d.pickup()
    assert d.status == DeliveryStatus.EN_ROUTE_TO_DELIVERY
    assert d.actual_pickup_time is not None

    # Arrive at delivery
    d.arrive_at_delivery()
    assert d.status == DeliveryStatus.AT_DELIVERY

    # Deliver
    d.deliver("http://proof.url")
    assert d.status == DeliveryStatus.DELIVERED
    assert d.actual_delivery_time is not None
    assert d.proof_of_delivery_url == "http://proof.url"


def test_invalid_delivery_state_transitions():
    d = Delivery.create(uuid.uuid4(), uuid.uuid4(), "Pickup", "Delivery")

    with pytest.raises(ValidationException):
        d.pickup()


def test_partner_toggles():
    account_id = uuid.uuid4()
    p = DeliveryPartner.register(
        account_id=account_id,
        name="John Doe",
        phone="555-0199",
        vehicle_type=VehicleType.MOTORCYCLE,
    )

    assert not p.is_online
    assert p.is_available

    p.toggle_online(True)
    assert p.is_online

    p.toggle_availability(False)
    assert not p.is_available
