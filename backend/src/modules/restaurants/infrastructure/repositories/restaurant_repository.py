import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.restaurants.application.ports.restaurant_repository import RestaurantRepository
from modules.restaurants.domain.entities.restaurant import Restaurant
from modules.restaurants.domain.value_objects.operating_hours import OperatingHours
from modules.restaurants.infrastructure.models.restaurant_model import RestaurantModel
from shared.domain.value_objects import Address


class SqlAlchemyRestaurantRepository(RestaurantRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, restaurant: Restaurant) -> None:
        model = RestaurantModel(
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
            operating_hours={day: dict(times) for day, times in restaurant.operating_hours.schedule.items()},
            is_active=restaurant.is_active,
            is_verified=restaurant.is_verified,
            rating_avg=restaurant.rating_avg,
            total_reviews=restaurant.total_reviews,
            created_at=restaurant.created_at,
            updated_at=restaurant.updated_at,
        )
        self._session.add(model)

    async def get_by_id(self, restaurant_id: uuid.UUID) -> Restaurant | None:
        result = await self._session.execute(select(RestaurantModel).where(RestaurantModel.id == restaurant_id))
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_domain(model)

    async def update(self, restaurant: Restaurant) -> None:
        result = await self._session.execute(select(RestaurantModel).where(RestaurantModel.id == restaurant.id))
        model = result.scalar_one_or_none()
        if model:
            model.name = restaurant.name
            model.description = restaurant.description
            model.cuisine_types = restaurant.cuisine_types
            model.address_street = restaurant.address.street
            model.address_city = restaurant.address.city
            model.address_state = restaurant.address.state
            model.address_postal_code = restaurant.address.postal_code
            model.address_country = restaurant.address.country
            model.address_latitude = restaurant.address.latitude
            model.address_longitude = restaurant.address.longitude
            model.phone = restaurant.phone
            model.email = restaurant.email
            model.operating_hours = {day: dict(times) for day, times in restaurant.operating_hours.schedule.items()}
            model.is_active = restaurant.is_active
            model.is_verified = restaurant.is_verified
            model.rating_avg = restaurant.rating_avg
            model.total_reviews = restaurant.total_reviews
            model.updated_at = restaurant.updated_at

    @staticmethod
    def _escape_like(value: str) -> str:
        return value.replace("%", r"\%").replace("_", r"\_")

    async def list_all(self, skip: int = 0, limit: int = 10, search: str | None = None) -> list[Restaurant]:
        query = select(RestaurantModel)
        if search:
            escaped = self._escape_like(search)
            query = query.where(
                (RestaurantModel.name.ilike(f"%{escaped}%")) | (RestaurantModel.description.ilike(f"%{escaped}%"))
            )
        query = query.order_by(RestaurantModel.created_at.desc()).offset(skip).limit(limit)
        result = await self._session.execute(query)
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]

    async def count_all(self, search: str | None = None) -> int:
        query = select(func.count(RestaurantModel.id))
        if search:
            escaped = self._escape_like(search)
            query = query.where(
                (RestaurantModel.name.ilike(f"%{escaped}%")) | (RestaurantModel.description.ilike(f"%{escaped}%"))
            )
        result = await self._session.execute(query)
        return result.scalar_one()

    def _to_domain(self, model: RestaurantModel) -> Restaurant:
        address = Address(
            street=model.address_street,
            city=model.address_city,
            state=model.address_state,
            postal_code=model.address_postal_code,
            country=model.address_country,
            latitude=model.address_latitude,
            longitude=model.address_longitude,
        )
        operating_hours = OperatingHours(schedule=model.operating_hours)

        return Restaurant(
            id=model.id,
            owner_id=model.owner_id,
            name=model.name,
            description=model.description,
            cuisine_types=model.cuisine_types,
            address=address,
            phone=model.phone,
            email=model.email,
            operating_hours=operating_hours,
            is_active=model.is_active,
            is_verified=model.is_verified,
            rating_avg=float(model.rating_avg),
            total_reviews=model.total_reviews,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
