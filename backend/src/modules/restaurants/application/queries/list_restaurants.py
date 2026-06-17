from dataclasses import dataclass

from modules.restaurants.application.ports.restaurant_repository import RestaurantRepository
from modules.restaurants.application.queries.get_restaurant import RestaurantDTO


@dataclass(frozen=True)
class ListRestaurantsQuery:
    skip: int = 0
    limit: int = 10
    search: str | None = None


@dataclass(frozen=True)
class ListRestaurantsResult:
    items: list[RestaurantDTO]
    total: int


class ListRestaurantsHandler:
    def __init__(self, restaurant_repo: RestaurantRepository) -> None:
        self._restaurant_repo = restaurant_repo

    async def handle(self, query: ListRestaurantsQuery) -> ListRestaurantsResult:
        restaurants = await self._restaurant_repo.list_all(
            skip=query.skip,
            limit=query.limit,
            search=query.search,
        )
        total = await self._restaurant_repo.count_all(search=query.search)

        dtos = [
            RestaurantDTO(
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
            for restaurant in restaurants
        ]

        return ListRestaurantsResult(items=dtos, total=total)
