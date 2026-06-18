import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class RegisterPartnerRequest(BaseModel):
    name: str = Field(..., max_length=255)
    phone: str = Field(..., max_length=50)
    vehicle_type: str = Field("MOTORCYCLE", max_length=50, description="Vehicle type: BICYCLE, MOTORCYCLE, CAR")


class PartnerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    account_id: uuid.UUID
    name: str
    phone: str
    vehicle_type: str
    is_online: bool
    is_available: bool
    rating_avg: Decimal
    total_deliveries: int


class UpdatePartnerLocationRequest(BaseModel):
    latitude: Decimal = Field(..., ge=-90, le=90)
    longitude: Decimal = Field(..., ge=-180, le=180)


class ToggleAvailabilityRequest(BaseModel):
    is_available: bool


class ToggleOnlineRequest(BaseModel):
    is_online: bool


class DeliveryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    order_id: uuid.UUID
    restaurant_id: uuid.UUID
    partner_id: uuid.UUID | None
    pickup_address: str
    delivery_address: str
    status: str
    estimated_pickup_time: datetime | None
    actual_pickup_time: datetime | None
    estimated_delivery_time: datetime | None
    actual_delivery_time: datetime | None
    distance_km: Decimal | None
    current_location_lat: float | None
    current_location_lon: float | None
    pickup_location_lat: float | None
    pickup_location_lon: float | None
    proof_of_delivery_url: str | None


class UpdateDeliveryStatusRequest(BaseModel):
    status: str = Field(
        ...,
        description="PARTNER_EN_ROUTE_TO_PICKUP, AT_PICKUP, EN_ROUTE_TO_DELIVERY, AT_DELIVERY, DELIVERED",
    )
    proof_of_delivery_url: str | None = None


class PartnerLocationResponse(BaseModel):
    partner_id: uuid.UUID
    latitude: float
    longitude: float


class AssignPartnerRequest(BaseModel):
    initial_radius_km: float | None = Field(None, gt=0)
    max_radius_km: float | None = Field(None, gt=0)
