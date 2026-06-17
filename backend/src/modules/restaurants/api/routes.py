import uuid
from typing import Any

from fastapi import APIRouter, Depends, Query, status

from modules.restaurants.api.dependencies import (
    get_list_restaurants_query_handler,
    get_register_restaurant_handler,
    get_restaurant_query_handler,
    get_update_restaurant_handler,
    get_verify_restaurant_handler,
)
from modules.restaurants.api.schemas import (
    RegisterRestaurantRequest,
    RestaurantListResponse,
    RestaurantResponse,
    UpdateRestaurantRequest,
)
from modules.restaurants.application.commands.register_restaurant import (
    RegisterRestaurantCommand,
    RegisterRestaurantHandler,
)
from modules.restaurants.application.commands.update_restaurant import (
    UpdateRestaurantCommand,
    UpdateRestaurantHandler,
)
from modules.restaurants.application.commands.verify_restaurant import (
    VerifyRestaurantCommand,
    VerifyRestaurantHandler,
)
from modules.restaurants.application.queries.get_restaurant import GetRestaurantHandler, GetRestaurantQuery
from modules.restaurants.application.queries.list_restaurants import ListRestaurantsHandler, ListRestaurantsQuery
from shared.api.response import ResponseEnvelope
from shared.api.security import require_restaurant_access, require_roles

router = APIRouter()
admin_router = APIRouter()


@router.post("", response_model=ResponseEnvelope[RestaurantResponse], status_code=status.HTTP_201_CREATED)
async def register_restaurant(
    request: RegisterRestaurantRequest,
    current_user: dict[str, Any] = Depends(require_roles("RESTAURANT_OWNER", "SUPER_ADMIN")),
    handler: RegisterRestaurantHandler = Depends(get_register_restaurant_handler),
    query_handler: GetRestaurantHandler = Depends(get_restaurant_query_handler),
) -> ResponseEnvelope[RestaurantResponse]:
    owner_id = uuid.UUID(current_user["sub"])
    command = RegisterRestaurantCommand(
        owner_id=owner_id,
        name=request.name,
        phone=request.phone,
        email=request.email,
        address_street=request.address_street,
        address_city=request.address_city,
        address_state=request.address_state,
        address_postal_code=request.address_postal_code,
        address_country=request.address_country,
        operating_hours=request.operating_hours,
        address_latitude=request.address_latitude,
        address_longitude=request.address_longitude,
        description=request.description,
        cuisine_types=request.cuisine_types,
    )
    restaurant_id = await handler.handle(command)

    dto = await query_handler.handle(GetRestaurantQuery(restaurant_id=restaurant_id))
    return ResponseEnvelope(data=RestaurantResponse.model_validate(dto))


@router.get("", response_model=ResponseEnvelope[RestaurantListResponse], status_code=status.HTTP_200_OK)
async def list_restaurants(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: str | None = Query(None),
    query_handler: ListRestaurantsHandler = Depends(get_list_restaurants_query_handler),
) -> ResponseEnvelope[RestaurantListResponse]:
    query = ListRestaurantsQuery(skip=skip, limit=limit, search=search)
    res = await query_handler.handle(query)

    items_response = [RestaurantResponse.model_validate(item) for item in res.items]
    return ResponseEnvelope(
        data=RestaurantListResponse(
            items=items_response,
            total=res.total,
        )
    )


@router.get("/{restaurant_id}", response_model=ResponseEnvelope[RestaurantResponse], status_code=status.HTTP_200_OK)
async def get_restaurant(
    restaurant_id: uuid.UUID,
    query_handler: GetRestaurantHandler = Depends(get_restaurant_query_handler),
) -> ResponseEnvelope[RestaurantResponse]:
    query = GetRestaurantQuery(restaurant_id=restaurant_id)
    dto = await query_handler.handle(query)
    return ResponseEnvelope(data=RestaurantResponse.model_validate(dto))


@router.patch("/{restaurant_id}", response_model=ResponseEnvelope[dict], status_code=status.HTTP_200_OK)
async def update_restaurant(
    restaurant_id: uuid.UUID,
    request: UpdateRestaurantRequest,
    authorized_id: uuid.UUID = Depends(require_restaurant_access),
    handler: UpdateRestaurantHandler = Depends(get_update_restaurant_handler),
) -> ResponseEnvelope[dict]:
    command = UpdateRestaurantCommand(
        restaurant_id=restaurant_id,
        name=request.name,
        phone=request.phone,
        email=request.email,
        address_street=request.address_street,
        address_city=request.address_city,
        address_state=request.address_state,
        address_postal_code=request.address_postal_code,
        address_country=request.address_country,
        operating_hours=request.operating_hours,
        address_latitude=request.address_latitude,
        address_longitude=request.address_longitude,
        description=request.description,
        cuisine_types=request.cuisine_types,
    )
    await handler.handle(command)
    return ResponseEnvelope(data={"message": "Restaurant details updated successfully"})


@admin_router.post("/{restaurant_id}/verify", response_model=ResponseEnvelope[dict], status_code=status.HTTP_200_OK)
async def verify_restaurant(
    restaurant_id: uuid.UUID,
    current_user: dict[str, Any] = Depends(require_roles("SUPER_ADMIN")),
    handler: VerifyRestaurantHandler = Depends(get_verify_restaurant_handler),
) -> ResponseEnvelope[dict]:
    command = VerifyRestaurantCommand(restaurant_id=restaurant_id)
    await handler.handle(command)
    return ResponseEnvelope(data={"message": "Restaurant verified successfully"})
