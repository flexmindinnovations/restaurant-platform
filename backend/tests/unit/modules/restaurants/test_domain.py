import pytest
import uuid

from modules.restaurants.domain.entities.restaurant import Restaurant
from shared.domain.value_objects import Address
from modules.restaurants.domain.value_objects.operating_hours import OperatingHours
from shared.domain.exceptions import ValidationException


@pytest.mark.unit
def test_address_creation():
    address = Address(
        street="123 Main St",
        city="Springfield",
        state="IL",
        postal_code="62701",
        country="USA",
        latitude=39.7817,
        longitude=-89.6501,
    )
    assert address.street == "123 Main St"
    assert address.latitude == 39.7817


@pytest.mark.unit
def test_operating_hours_valid():
    schedule = {
        "monday": {"open": "09:00", "close": "22:00"},
        "saturday": {"open": "10:00", "close": "23:30"},
    }
    oh = OperatingHours(schedule=schedule)
    assert oh.schedule == schedule


@pytest.mark.unit
def test_operating_hours_invalid():
    invalid_schedules = [
        {},  # empty
        {"monday": {"open": "09:00"}},  # missing close
        {"monday": {"close": "22:00"}},  # missing open
        {"invalidday": {"open": "09:00", "close": "22:00"}},  # invalid day
        {"monday": {"open": "9:00", "close": "22:00"}},  # invalid time format
        {"monday": {"open": "09:00", "close": "26:00"}},  # invalid hour
    ]
    for sched in invalid_schedules:
        with pytest.raises(ValidationException):
            OperatingHours(schedule=sched)


@pytest.mark.unit
def test_restaurant_registration():
    owner_id = uuid.uuid4()
    address = Address("Street", "City", "State", "Zip", "Country")
    oh = OperatingHours({"monday": {"open": "09:00", "close": "22:00"}})
    
    restaurant = Restaurant.register(
        owner_id=owner_id,
        name="Taco Palace",
        address=address,
        phone="+1234567890",
        email="info@tacopalace.com",
        operating_hours=oh,
        description="Best tacos in town",
        cuisine_types=["Mexican", "Fast Food"],
    )
    
    assert restaurant.name == "Taco Palace"
    assert restaurant.owner_id == owner_id
    assert restaurant.address == address
    assert restaurant.phone == "+1234567890"
    assert restaurant.email == "info@tacopalace.com"
    assert restaurant.operating_hours == oh
    assert restaurant.description == "Best tacos in town"
    assert restaurant.cuisine_types == ["Mexican", "Fast Food"]
    assert restaurant.is_active is True
    assert restaurant.is_verified is False
    
    events = restaurant.collect_events()
    assert len(events) == 1
    assert events[0].name == "Taco Palace"


@pytest.mark.unit
def test_restaurant_update():
    owner_id = uuid.uuid4()
    address = Address("Street", "City", "State", "Zip", "Country")
    oh = OperatingHours({"monday": {"open": "09:00", "close": "22:00"}})
    
    restaurant = Restaurant.register(
        owner_id=owner_id,
        name="Taco Palace",
        address=address,
        phone="+1234567890",
        email="info@tacopalace.com",
        operating_hours=oh,
    )
    
    new_address = Address("Street 2", "City", "State", "Zip", "Country")
    restaurant.update_details(
        name="Taco Express",
        description="Fast tacos",
        address=new_address,
    )
    
    assert restaurant.name == "Taco Express"
    assert restaurant.description == "Fast tacos"
    assert restaurant.address == new_address


@pytest.mark.unit
def test_restaurant_verify_and_deactivate():
    owner_id = uuid.uuid4()
    address = Address("Street", "City", "State", "Zip", "Country")
    oh = OperatingHours({"monday": {"open": "09:00", "close": "22:00"}})
    
    restaurant = Restaurant.register(
        owner_id=owner_id,
        name="Taco Palace",
        address=address,
        phone="+1234567890",
        email="info@tacopalace.com",
        operating_hours=oh,
    )
    
    assert restaurant.is_verified is False
    restaurant.verify()
    assert restaurant.is_verified is True
    
    assert restaurant.is_active is True
    restaurant.deactivate()
    assert restaurant.is_active is False
    
    # Cannot update deactivated restaurant
    with pytest.raises(ValidationException):
        restaurant.update_details(name="Failed")
