import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CreatePromotionRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=50)
    description: str = Field("", max_length=500)
    promotion_type: str = Field(..., description="PERCENTAGE, FIXED_AMOUNT, FREE_DELIVERY, or BUY_X_GET_Y")
    value: Decimal = Field(..., gt=0)
    valid_from: datetime
    valid_until: datetime
    min_order_amount: Decimal | None = Field(None, ge=0)
    max_discount_amount: Decimal | None = Field(None, ge=0)
    currency: str = Field("USD", max_length=3)
    max_total_uses: int | None = Field(None, ge=1)
    max_uses_per_customer: int = Field(1, ge=1)
    restaurant_id: uuid.UUID | None = None


class ApplyPromotionRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=50)
    order_amount: Decimal = Field(..., gt=0)
    currency: str = Field("USD", max_length=3)


class ValidatePromotionRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=50)
    order_amount: Decimal = Field(..., gt=0)
    currency: str = Field("USD", max_length=3)


class PromotionResponse(BaseModel):
    id: uuid.UUID
    code: str
    description: str
    promotion_type: str
    value: Decimal
    min_order_amount: Decimal | None
    min_order_currency: str | None
    max_discount_amount: Decimal | None
    max_discount_currency: str | None
    valid_from: datetime
    valid_until: datetime
    max_total_uses: int | None
    max_uses_per_customer: int
    total_uses: int
    status: str
    restaurant_id: uuid.UUID | None
    is_valid: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PromotionListResponse(BaseModel):
    items: list[PromotionResponse]
    total: int


class ApplyPromotionResponse(BaseModel):
    promotion_id: uuid.UUID
    discount_amount: Decimal
    discount_currency: str


class ValidatePromotionResponse(BaseModel):
    is_valid: bool
    discount_amount: Decimal
    discount_currency: str
    promotion_type: str
    description: str
