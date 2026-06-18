import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from modules.orders.domain.value_objects.order_status import OrderStatus

# --- Cart Schemas ---


class AddToCartRequest(BaseModel):
    menu_item_id: uuid.UUID
    quantity: int = Field(..., ge=1, description="Quantity must be at least 1")
    special_instructions: str | None = Field(None, max_length=500)


class UpdateCartItemRequest(BaseModel):
    quantity: int = Field(..., ge=0, description="Quantity to update, 0 will remove item")


class CartItemResponse(BaseModel):
    id: uuid.UUID
    menu_item_id: uuid.UUID
    name: str
    unit_price_amount: Decimal
    unit_price_currency: str
    quantity: int
    special_instructions: str | None
    subtotal_amount: Decimal

    model_config = ConfigDict(from_attributes=True)


class CartResponse(BaseModel):
    customer_id: uuid.UUID
    restaurant_id: uuid.UUID | None
    items: list[CartItemResponse]
    total_amount: Decimal
    currency: str

    model_config = ConfigDict(from_attributes=True)


# --- Order Schemas ---


class PlaceOrderRequest(BaseModel):
    delivery_address_street: str = Field(..., min_length=1, max_length=255)
    delivery_address_city: str = Field(..., min_length=1, max_length=100)
    delivery_address_state: str = Field(..., min_length=1, max_length=100)
    delivery_address_postal_code: str = Field(..., min_length=1, max_length=20)
    delivery_address_country: str = Field(..., min_length=1, max_length=100)
    tip_amount: Decimal = Field(Decimal("0.00"), ge=0, description="Tip amount must be non-negative")
    delivery_notes: str | None = Field(None, max_length=500)


class PlaceOrderResponse(BaseModel):
    order_id: uuid.UUID


class OrderItemResponse(BaseModel):
    id: uuid.UUID
    menu_item_id: uuid.UUID
    name: str
    unit_price_amount: Decimal
    unit_price_currency: str
    quantity: int
    special_instructions: str | None
    subtotal_amount: Decimal

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    id: uuid.UUID
    restaurant_id: uuid.UUID
    customer_id: uuid.UUID
    order_number: str
    status: str
    delivery_address_street: str
    delivery_address_city: str
    delivery_address_state: str
    delivery_address_postal_code: str
    delivery_address_country: str
    delivery_notes: str | None
    subtotal_amount: Decimal
    subtotal_currency: str
    tax_amount: Decimal
    tax_currency: str
    delivery_fee_amount: Decimal
    delivery_fee_currency: str
    tip_amount: Decimal
    tip_currency: str
    total_amount: Decimal
    total_currency: str
    cancellation_reason: str | None
    placed_at: datetime
    confirmed_at: datetime | None
    preparing_at: datetime | None
    ready_at: datetime | None
    picked_up_at: datetime | None
    delivered_at: datetime | None
    cancelled_at: datetime | None
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemResponse]

    model_config = ConfigDict(from_attributes=True)


class OrderListResponse(BaseModel):
    items: list[OrderResponse]
    total: int


class CancelOrderRequest(BaseModel):
    reason: str = Field(..., min_length=1, max_length=500)


class UpdateOrderStatusRequest(BaseModel):
    status: OrderStatus
