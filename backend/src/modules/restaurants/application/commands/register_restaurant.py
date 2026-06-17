import uuid
from dataclasses import dataclass
from typing import Any

from modules.restaurants.application.ports.restaurant_repository import RestaurantRepository
from modules.restaurants.domain.entities.restaurant import Restaurant
from shared.domain.value_objects import Address
from modules.restaurants.domain.value_objects.operating_hours import OperatingHours
from shared.application.ports.unit_of_work import AbstractUnitOfWork


@dataclass(frozen=True)
class RegisterRestaurantCommand:
    owner_id: uuid.UUID
    name: str
    phone: str
    email: str
    address_street: str
    address_city: str
    address_state: str
    address_postal_code: str
    address_country: str
    operating_hours: dict[str, Any]
    address_latitude: float | None = None
    address_longitude: float | None = None
    description: str | None = None
    cuisine_types: list[str] | None = None


class RegisterRestaurantHandler:
    def __init__(self, restaurant_repo: RestaurantRepository, uow: AbstractUnitOfWork) -> None:
        self._restaurant_repo = restaurant_repo
        self._uow = uow

    async def handle(self, command: RegisterRestaurantCommand) -> uuid.UUID:
        address = Address(
            street=command.address_street,
            city=command.address_city,
            state=command.address_state,
            postal_code=command.address_postal_code,
            country=command.address_country,
            latitude=command.address_latitude,
            longitude=command.address_longitude,
        )
        operating_hours = OperatingHours(schedule=command.operating_hours)

        restaurant = Restaurant.register(
            owner_id=command.owner_id,
            name=command.name,
            address=address,
            phone=command.phone,
            email=command.email,
            operating_hours=operating_hours,
            description=command.description,
            cuisine_types=command.cuisine_types,
        )

        async with self._uow:
            await self._restaurant_repo.add(restaurant)
            self._uow.register_aggregate(restaurant)
            await self._uow.commit()

        return restaurant.id
