import uuid
from dataclasses import dataclass
from typing import Any

from modules.restaurants.application.ports.restaurant_repository import RestaurantRepository
from modules.restaurants.domain.value_objects.operating_hours import OperatingHours
from shared.application.ports.unit_of_work import AbstractUnitOfWork
from shared.domain.exceptions import NotFoundException
from shared.domain.value_objects import Address


@dataclass(frozen=True)
class UpdateRestaurantCommand:
    restaurant_id: uuid.UUID
    name: str | None = None
    phone: str | None = None
    email: str | None = None
    address_street: str | None = None
    address_city: str | None = None
    address_state: str | None = None
    address_postal_code: str | None = None
    address_country: str | None = None
    operating_hours: dict[str, Any] | None = None
    address_latitude: float | None = None
    address_longitude: float | None = None
    description: str | None = None
    cuisine_types: list[str] | None = None


class UpdateRestaurantHandler:
    def __init__(self, restaurant_repo: RestaurantRepository, uow: AbstractUnitOfWork) -> None:
        self._restaurant_repo = restaurant_repo
        self._uow = uow

    async def handle(self, command: UpdateRestaurantCommand) -> None:
        restaurant = await self._restaurant_repo.get_by_id(command.restaurant_id)
        if not restaurant:
            raise NotFoundException("Restaurant not found")

        # Create updated address value object if any address fields are updated
        address = None
        if any([
            command.address_street,
            command.address_city,
            command.address_state,
            command.address_postal_code,
            command.address_country,
            command.address_latitude is not None,
            command.address_longitude is not None,
        ]):
            current_address = restaurant.address
            ca = current_address
            address = Address(
                street=command.address_street if command.address_street is not None else ca.street,
                city=command.address_city if command.address_city is not None else ca.city,
                state=command.address_state if command.address_state is not None else ca.state,
                postal_code=command.address_postal_code or ca.postal_code,
                country=command.address_country if command.address_country is not None else ca.country,
                latitude=command.address_latitude if command.address_latitude is not None else ca.latitude,
                longitude=command.address_longitude if command.address_longitude is not None else ca.longitude,
            )

        operating_hours = None
        if command.operating_hours is not None:
            operating_hours = OperatingHours(schedule=command.operating_hours)

        restaurant.update_details(
            name=command.name,
            description=command.description,
            cuisine_types=command.cuisine_types,
            address=address,
            phone=command.phone,
            email=command.email,
            operating_hours=operating_hours,
        )

        async with self._uow:
            await self._restaurant_repo.update(restaurant)
            self._uow.register_aggregate(restaurant)
            await self._uow.commit()
