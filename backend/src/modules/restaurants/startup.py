import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.restaurants.infrastructure.models.restaurant_model import RestaurantModel
from shared.api.security import register_ownership_checker


async def _check_restaurant_ownership(restaurant_id: uuid.UUID, session: AsyncSession) -> uuid.UUID | None:
    result = await session.execute(
        select(RestaurantModel.owner_id).where(RestaurantModel.id == restaurant_id)
    )
    row = result.scalar_one_or_none()
    return row


def register_restaurants_hooks() -> None:
    register_ownership_checker(_check_restaurant_ownership)
