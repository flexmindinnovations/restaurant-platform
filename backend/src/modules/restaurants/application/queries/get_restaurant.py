import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from modules.restaurants.application.ports.restaurant_repository import RestaurantRepository
from shared.domain.exceptions import NotFoundException


@dataclass(frozen=True)
class GetRestaurantQuery:
    restaurant_id: uuid.UUID


@dataclass(frozen=True)
class RestaurantDTO:
    id: uuid.UUID
    owner_id: uuid.UUID
    name: str
    description: str | None
    cuisine_types: list[str]
    address_street: str
    address_city: str
    address_state: str
    address_postal_code: str
    address_country: str
    address_latitude: float | None
    address_longitude: float | None
    phone: str
    email: str
    operating_hours: dict[str, Any]
    is_active: bool
    is_verified: bool
    rating_avg: float
    total_reviews: int
    created_at: datetime
    updated_at: datetime


class GetRestaurantHandler:
    def __init__(self, restaurant_repo: RestaurantRepository) -> None:
        self._restaurant_repo = restaurant_repo

    async def handle(self, query: GetRestaurantQuery) -> RestaurantDTO:
        restaurant = await self._restaurant_repo.get_by_id(query.restaurant_id)
        if not restaurant:
            raise NotFoundException("Restaurant not found")

        return RestaurantDTO(
            id=restaurant.id,
            owner_id=restaurant.owner_id,
            name=restaurant.name,
            description=restaurant.description,
            cuisine_types=restaurant.cuisine_types,
            address_street=restaurant.address.street,
            address_city=restaurant.address.city,
            address_state=restaurant.address.state,
            address_postal_code=restaurant.address.postal_code,
            address_country=restaurant.address.country,
            address_latitude=restaurant.address.latitude,
            address_longitude=restaurant.address.longitude,
            phone=restaurant.phone,
            email=restaurant.email,
            operating_hours=restaurant.operating_hours.schedule,
            is_active=restaurant.is_active,
            is_verified=restaurant.is_verified,
            rating_avg=restaurant.rating_avg,
            total_reviews=restaurant.total_reviews,
            created_at=restaurant.created_at,
            updated_at=restaurant.updated_at,
        )
