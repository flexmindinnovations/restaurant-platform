import uuid

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db_session
from modules.menus.infrastructure.models.menu_models import MenuItemModel
from modules.restaurants.infrastructure.models.restaurant_model import RestaurantModel
from shared.api.response import ResponseEnvelope

recommendations_router = APIRouter()


class RecommendedRestaurant(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    cuisine_types: list[str]
    address_city: str
    rating_avg: float
    total_reviews: int


class RestaurantRecommendationsResponse(BaseModel):
    restaurants: list[RecommendedRestaurant]


class RecommendedMenuItem(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    price_amount: float
    price_currency: str
    restaurant_id: uuid.UUID
    image_url: str | None


class MenuItemRecommendationsResponse(BaseModel):
    menu_items: list[RecommendedMenuItem]


@recommendations_router.get("/restaurants", response_model=ResponseEnvelope[RestaurantRecommendationsResponse])
async def get_restaurant_recommendations(
    _customer_id: uuid.UUID | None = Query(None),
    latitude: float | None = Query(None),
    longitude: float | None = Query(None),
    limit: int = Query(5, ge=1, le=50),
    session: AsyncSession = Depends(get_db_session),
) -> ResponseEnvelope[RestaurantRecommendationsResponse]:
    stmt = select(RestaurantModel).where(RestaurantModel.is_active.is_(True))

    if latitude is not None and longitude is not None:
        distance = func.power(RestaurantModel.address_latitude - latitude, 2) + func.power(
            RestaurantModel.address_longitude - longitude, 2
        )
        stmt = stmt.order_by(distance.asc(), RestaurantModel.rating_avg.desc())
    else:
        stmt = stmt.order_by(RestaurantModel.rating_avg.desc())

    stmt = stmt.limit(limit)
    result = await session.execute(stmt)
    restaurants = result.scalars().all()

    res = [
        RecommendedRestaurant(
            id=r.id,
            name=r.name,
            description=r.description,
            cuisine_types=r.cuisine_types or [],
            address_city=r.address_city,
            rating_avg=float(r.rating_avg),
            total_reviews=r.total_reviews,
        )
        for r in restaurants
    ]
    return ResponseEnvelope(data=RestaurantRecommendationsResponse(restaurants=res))


@recommendations_router.get("/menu-items", response_model=ResponseEnvelope[MenuItemRecommendationsResponse])
async def get_menu_item_recommendations(
    _customer_id: uuid.UUID | None = Query(None),
    restaurant_id: uuid.UUID | None = Query(None),
    limit: int = Query(5, ge=1, le=50),
    session: AsyncSession = Depends(get_db_session),
) -> ResponseEnvelope[MenuItemRecommendationsResponse]:
    stmt = select(MenuItemModel).where(MenuItemModel.is_available.is_(True))

    if restaurant_id is not None:
        stmt = stmt.where(MenuItemModel.restaurant_id == restaurant_id)

    stmt = stmt.order_by(MenuItemModel.display_order.asc()).limit(limit)
    result = await session.execute(stmt)
    items = result.scalars().all()

    res = [
        RecommendedMenuItem(
            id=item.id,
            name=item.name,
            description=item.description,
            price_amount=float(item.price_amount),
            price_currency=item.price_currency,
            restaurant_id=item.restaurant_id,
            image_url=item.image_url,
        )
        for item in items
    ]
    return ResponseEnvelope(data=MenuItemRecommendationsResponse(menu_items=res))
