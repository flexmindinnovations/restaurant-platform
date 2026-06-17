import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRestaurantRequest(BaseModel):
    name: str = Field(..., max_length=255)
    description: str | None = None
    cuisine_types: list[str] = Field(default_factory=list)
    address_street: str = Field(..., max_length=255)
    address_city: str = Field(..., max_length=100)
    address_state: str = Field(..., max_length=100)
    address_postal_code: str = Field(..., max_length=20)
    address_country: str = Field(..., max_length=100)
    address_latitude: float | None = None
    address_longitude: float | None = None
    phone: str = Field(..., max_length=50)
    email: EmailStr
    operating_hours: dict[str, dict[str, str]] = Field(default_factory=dict)


class UpdateRestaurantRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    cuisine_types: list[str] | None = None
    address_street: str | None = None
    address_city: str | None = None
    address_state: str | None = None
    address_postal_code: str | None = None
    address_country: str | None = None
    address_latitude: float | None = None
    address_longitude: float | None = None
    phone: str | None = None
    email: EmailStr | None = None
    operating_hours: dict[str, dict[str, str]] | None = None


class RestaurantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    owner_id: uuid.UUID
    name: str
    description: str | None
    cuisine_types: list[str]
    address_street: str
    address_city: str
    address_state: str
    address_postal_code: str
    address_country: str
    address_latitude: float | None
    address_longitude: float | None
    phone: str
    email: str
    operating_hours: dict[str, dict[str, str]]
    is_active: bool
    is_verified: bool
    rating_avg: float
    total_reviews: int
    created_at: datetime
    updated_at: datetime


class RestaurantListResponse(BaseModel):
    items: list[RestaurantResponse]
    total: int
