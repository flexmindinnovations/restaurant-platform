import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class AddPaymentMethodRequest(BaseModel):
    type: str = Field(..., max_length=50, description="Payment method type e.g. CARD")
    last_four: str | None = Field(None, max_length=4)
    brand: str | None = Field(None, max_length=50)
    is_default: bool = False
    token: str = Field(..., max_length=255, description="Tokenized payment reference from gateway")


class PaymentMethodResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    customer_id: uuid.UUID
    type: str
    last_four: str | None
    brand: str | None
    is_default: bool


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    order_id: uuid.UUID
    customer_id: uuid.UUID
    restaurant_id: uuid.UUID
    amount_amount: Decimal
    amount_currency: str
    status: str
    payment_method_type: str
    payment_method_id: uuid.UUID | None
    gateway_transaction_id: str | None
    failure_reason: str | None
    captured_at: datetime | None
    refunded_at: datetime | None
    created_at: datetime
    updated_at: datetime


class RefundPaymentRequest(BaseModel):
    amount: Decimal | None = Field(None, gt=0, decimal_places=2)
