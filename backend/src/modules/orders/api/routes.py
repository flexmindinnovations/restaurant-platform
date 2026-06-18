import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db_session
from modules.orders.api.dependencies import (
    get_add_to_cart_handler,
    get_cancel_order_handler,
    get_cart_query_handler,
    get_clear_cart_handler,
    get_confirm_order_handler,
    get_list_customer_orders_handler,
    get_list_restaurant_orders_handler,
    get_order_query_handler,
    get_place_order_handler,
    get_remove_from_cart_handler,
    get_update_cart_item_handler,
    get_update_order_status_handler,
)
from modules.orders.api.schemas import (
    AddToCartRequest,
    CancelOrderRequest,
    CartResponse,
    OrderListResponse,
    OrderResponse,
    PlaceOrderRequest,
    PlaceOrderResponse,
    UpdateCartItemRequest,
    UpdateOrderStatusRequest,
)
from modules.orders.application.commands.add_to_cart import AddToCartCommand, AddToCartHandler
from modules.orders.application.commands.cancel_order import CancelOrderCommand, CancelOrderHandler
from modules.orders.application.commands.clear_cart import ClearCartCommand, ClearCartHandler
from modules.orders.application.commands.confirm_order import ConfirmOrderCommand, ConfirmOrderHandler
from modules.orders.application.commands.place_order import PlaceOrderCommand, PlaceOrderHandler
from modules.orders.application.commands.remove_from_cart import RemoveFromCartCommand, RemoveFromCartHandler
from modules.orders.application.commands.update_cart_item import UpdateCartItemCommand, UpdateCartItemHandler
from modules.orders.application.commands.update_order_status import UpdateOrderStatusCommand, UpdateOrderStatusHandler
from modules.orders.application.queries.get_cart import GetCartHandler, GetCartQuery
from modules.orders.application.queries.get_order import GetOrderHandler, GetOrderQuery
from modules.orders.application.queries.list_customer_orders import ListCustomerOrdersHandler, ListCustomerOrdersQuery
from modules.orders.application.queries.list_restaurant_orders import (
    ListRestaurantOrdersHandler,
    ListRestaurantOrdersQuery,
)
from modules.orders.domain.value_objects.order_status import OrderStatus
from shared.api.response import ResponseEnvelope
from shared.api.security import get_current_user, require_restaurant_access, require_roles

router = APIRouter()
checkout_router = APIRouter()


# --- Checkout & Cart Router (/api/v1/checkout) ---


@checkout_router.get("/cart", response_model=ResponseEnvelope[CartResponse])
async def get_cart(
    current_user: dict[str, Any] = Depends(get_current_user),
    query_handler: GetCartHandler = Depends(get_cart_query_handler),
) -> ResponseEnvelope[CartResponse]:
    customer_id = uuid.UUID(current_user["sub"])
    dto = await query_handler.handle(GetCartQuery(customer_id=customer_id))
    return ResponseEnvelope(data=CartResponse.model_validate(dto))


@checkout_router.post("/cart/items", response_model=ResponseEnvelope[CartResponse], status_code=status.HTTP_201_CREATED)
async def add_to_cart(
    request: AddToCartRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    handler: AddToCartHandler = Depends(get_add_to_cart_handler),
    query_handler: GetCartHandler = Depends(get_cart_query_handler),
) -> ResponseEnvelope[CartResponse]:
    customer_id = uuid.UUID(current_user["sub"])
    command = AddToCartCommand(
        customer_id=customer_id,
        menu_item_id=request.menu_item_id,
        quantity=request.quantity,
        special_instructions=request.special_instructions,
    )
    await handler.handle(command)

    dto = await query_handler.handle(GetCartQuery(customer_id=customer_id))
    return ResponseEnvelope(data=CartResponse.model_validate(dto))


@checkout_router.patch("/cart/items/{menu_item_id}", response_model=ResponseEnvelope[CartResponse])
async def update_cart_item(
    menu_item_id: uuid.UUID,
    request: UpdateCartItemRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    handler: UpdateCartItemHandler = Depends(get_update_cart_item_handler),
    query_handler: GetCartHandler = Depends(get_cart_query_handler),
) -> ResponseEnvelope[CartResponse]:
    customer_id = uuid.UUID(current_user["sub"])
    command = UpdateCartItemCommand(
        customer_id=customer_id,
        menu_item_id=menu_item_id,
        quantity=request.quantity,
    )
    await handler.handle(command)

    dto = await query_handler.handle(GetCartQuery(customer_id=customer_id))
    return ResponseEnvelope(data=CartResponse.model_validate(dto))


@checkout_router.delete("/cart/items/{menu_item_id}", response_model=ResponseEnvelope[CartResponse])
async def remove_from_cart(
    menu_item_id: uuid.UUID,
    current_user: dict[str, Any] = Depends(get_current_user),
    handler: RemoveFromCartHandler = Depends(get_remove_from_cart_handler),
    query_handler: GetCartHandler = Depends(get_cart_query_handler),
) -> ResponseEnvelope[CartResponse]:
    customer_id = uuid.UUID(current_user["sub"])
    command = RemoveFromCartCommand(
        customer_id=customer_id,
        menu_item_id=menu_item_id,
    )
    await handler.handle(command)

    dto = await query_handler.handle(GetCartQuery(customer_id=customer_id))
    return ResponseEnvelope(data=CartResponse.model_validate(dto))


@checkout_router.delete("/cart/clear", response_model=ResponseEnvelope[dict])
async def clear_cart(
    current_user: dict[str, Any] = Depends(get_current_user),
    handler: ClearCartHandler = Depends(get_clear_cart_handler),
) -> ResponseEnvelope[dict]:
    customer_id = uuid.UUID(current_user["sub"])
    command = ClearCartCommand(customer_id=customer_id)
    await handler.handle(command)
    return ResponseEnvelope(data={"message": "Cart cleared successfully"})


@checkout_router.post(
    "/place-order",
    response_model=ResponseEnvelope[PlaceOrderResponse],
    status_code=status.HTTP_201_CREATED,
)
async def place_order(
    request: PlaceOrderRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    handler: PlaceOrderHandler = Depends(get_place_order_handler),
) -> ResponseEnvelope[PlaceOrderResponse]:
    customer_id = uuid.UUID(current_user["sub"])
    command = PlaceOrderCommand(
        customer_id=customer_id,
        delivery_address_street=request.delivery_address_street,
        delivery_address_city=request.delivery_address_city,
        delivery_address_state=request.delivery_address_state,
        delivery_address_postal_code=request.delivery_address_postal_code,
        delivery_address_country=request.delivery_address_country,
        tip_amount=request.tip_amount,
        delivery_notes=request.delivery_notes,
    )
    order_id = await handler.handle(command)
    return ResponseEnvelope(data=PlaceOrderResponse(order_id=order_id))


# --- Orders Management Router (/api/v1/orders) ---


@router.get("", response_model=ResponseEnvelope[OrderListResponse])
async def list_orders(
    restaurant_id: uuid.UUID | None = Query(None),
    status_filter: OrderStatus | None = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: dict[str, Any] = Depends(get_current_user),
    customer_handler: ListCustomerOrdersHandler = Depends(get_list_customer_orders_handler),
    restaurant_handler: ListRestaurantOrdersHandler = Depends(get_list_restaurant_orders_handler),
    session: AsyncSession = Depends(get_db_session),
) -> ResponseEnvelope[OrderListResponse]:
    # 1. Restaurant View (requires RESTAURANT_OWNER / RESTAURANT_STAFF roles and require_restaurant_access verification)
    if restaurant_id is not None:
        # Perform security scoping check
        await require_restaurant_access(restaurant_id, current_user, session)
        query = ListRestaurantOrdersQuery(
            restaurant_id=restaurant_id,
            status=status_filter,
            skip=skip,
            limit=limit,
        )
        res = await restaurant_handler.handle(query)
        items_response = [OrderResponse.model_validate(item) for item in res.items]
        return ResponseEnvelope(data=OrderListResponse(items=items_response, total=res.total))

    # 2. Customer View (defaults to checking current customer's order history)
    customer_id = uuid.UUID(current_user["sub"])
    query_cust = ListCustomerOrdersQuery(
        customer_id=customer_id,
        skip=skip,
        limit=limit,
    )
    res_cust = await customer_handler.handle(query_cust)
    items_response = [OrderResponse.model_validate(item) for item in res_cust.items]
    return ResponseEnvelope(data=OrderListResponse(items=items_response, total=res_cust.total))


@router.get("/{order_id}", response_model=ResponseEnvelope[OrderResponse])
async def get_order(
    order_id: uuid.UUID,
    current_user: dict[str, Any] = Depends(get_current_user),
    query_handler: GetOrderHandler = Depends(get_order_query_handler),
    session: AsyncSession = Depends(get_db_session),
) -> ResponseEnvelope[OrderResponse]:
    dto = await query_handler.handle(GetOrderQuery(order_id=order_id))

    # Security Scoping Checks
    user_id = uuid.UUID(current_user["sub"])
    user_roles = current_user.get("roles", [])

    is_customer = dto.customer_id == user_id
    is_super_admin = "SUPER_ADMIN" in user_roles

    if not is_customer and not is_super_admin:
        # Check if they are restaurant staff/owner for this order
        try:
            await require_restaurant_access(dto.restaurant_id, current_user, session)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access to this order is denied",
            ) from None

    return ResponseEnvelope(data=OrderResponse.model_validate(dto))


@router.post("/{order_id}/confirm", response_model=ResponseEnvelope[dict])
async def confirm_order(
    order_id: uuid.UUID,
    current_user: dict[str, Any] = Depends(require_roles("RESTAURANT_OWNER", "RESTAURANT_STAFF", "SUPER_ADMIN")),
    query_handler: GetOrderHandler = Depends(get_order_query_handler),
    handler: ConfirmOrderHandler = Depends(get_confirm_order_handler),
    session: AsyncSession = Depends(get_db_session),
) -> ResponseEnvelope[dict]:
    # 1. Fetch order details to retrieve restaurant ID
    dto = await query_handler.handle(GetOrderQuery(order_id=order_id))

    # 2. Check if user owns or is staff at this restaurant
    await require_restaurant_access(dto.restaurant_id, current_user, session)

    # 3. Confirm order
    command = ConfirmOrderCommand(order_id=order_id)
    await handler.handle(command)
    return ResponseEnvelope(data={"message": "Order confirmed successfully"})


@router.post("/{order_id}/status", response_model=ResponseEnvelope[dict])
async def update_order_status(
    order_id: uuid.UUID,
    request: UpdateOrderStatusRequest,
    current_user: dict[str, Any] = Depends(
        require_roles("RESTAURANT_OWNER", "RESTAURANT_STAFF", "SUPER_ADMIN", "DELIVERY_PARTNER")
    ),
    query_handler: GetOrderHandler = Depends(get_order_query_handler),
    handler: UpdateOrderStatusHandler = Depends(get_update_order_status_handler),
    session: AsyncSession = Depends(get_db_session),
) -> ResponseEnvelope[dict]:
    # 1. Fetch order details to retrieve restaurant ID
    dto = await query_handler.handle(GetOrderQuery(order_id=order_id))

    # 2. Verify restaurant scoping
    await require_restaurant_access(dto.restaurant_id, current_user, session)

    # 3. Transition status
    command = UpdateOrderStatusCommand(order_id=order_id, status=request.status)
    await handler.handle(command)
    return ResponseEnvelope(data={"message": f"Order status updated successfully to {request.status.value}"})


@router.post("/{order_id}/cancel", response_model=ResponseEnvelope[dict])
async def cancel_order(
    order_id: uuid.UUID,
    request: CancelOrderRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    query_handler: GetOrderHandler = Depends(get_order_query_handler),
    handler: CancelOrderHandler = Depends(get_cancel_order_handler),
    session: AsyncSession = Depends(get_db_session),
) -> ResponseEnvelope[dict]:
    # 1. Fetch order details to retrieve restaurant ID and customer ID
    dto = await query_handler.handle(GetOrderQuery(order_id=order_id))

    user_id = uuid.UUID(current_user["sub"])
    user_roles = current_user.get("roles", [])

    is_customer = dto.customer_id == user_id

    # 2. If not the customer, check restaurant scoping
    if not is_customer and "SUPER_ADMIN" not in user_roles:
        await require_restaurant_access(dto.restaurant_id, current_user, session)

    # 3. Execute cancellation command
    command = CancelOrderCommand(
        order_id=order_id,
        reason=request.reason,
        user_id=user_id,
        user_roles=user_roles,
    )
    await handler.handle(command)
    return ResponseEnvelope(data={"message": "Order cancelled successfully"})
