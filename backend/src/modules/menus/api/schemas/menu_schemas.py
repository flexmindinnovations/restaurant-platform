import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CreateMenuRequest(BaseModel):
    name: str = Field(..., max_length=255)
    description: str | None = None
    restaurant_id: uuid.UUID | None = None


class UpdateMenuRequest(BaseModel):
    name: str | None = Field(None, max_length=255)
    description: str | None = None
    is_active: bool | None = None


class CategoryRequest(BaseModel):
    name: str = Field(..., max_length=255)
    description: str | None = None
    display_order: int = 0


class UpdateCategoryRequest(BaseModel):
    name: str | None = Field(None, max_length=255)
    description: str | None = None
    display_order: int | None = None


class CreateMenuItemRequest(BaseModel):
    name: str = Field(..., max_length=255)
    description: str | None = None
    price_amount: Decimal = Field(..., gt=0, decimal_places=2)
    price_currency: str = Field("INR", max_length=3)
    category_id: uuid.UUID | None = None
    image_url: str | None = Field(None, max_length=500)
    display_order: int = 0
    dietary_labels: list[str] = Field(default_factory=list)
    preparation_time_minutes: int | None = Field(None, ge=0)


class UpdateMenuItemRequest(BaseModel):
    name: str | None = Field(None, max_length=255)
    description: str | None = None
    price_amount: Decimal | None = Field(None, gt=0, decimal_places=2)
    price_currency: str | None = Field(None, max_length=3)
    category_id: uuid.UUID | None = ...  # type: ignore[assignment]
    image_url: str | None = Field(None, max_length=500)
    display_order: int | None = None
    is_available: bool | None = None
    dietary_labels: list[str] | None = None
    preparation_time_minutes: int | None = Field(None, ge=0)


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    menu_id: uuid.UUID
    name: str
    description: str | None
    display_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    items: list["MenuItemResponse"] = Field(default_factory=list)


class MenuResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    restaurant_id: uuid.UUID
    name: str
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    categories: list[CategoryResponse] = Field(default_factory=list)


class MenuListResponse(BaseModel):
    items: list[MenuResponse]
    total: int


class MenuItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    menu_id: uuid.UUID
    category_id: uuid.UUID | None
    restaurant_id: uuid.UUID
    name: str
    description: str | None
    price_amount: Decimal
    price_currency: str
    image_url: str | None
    display_order: int
    is_available: bool
    dietary_labels: list[str]
    preparation_time_minutes: int | None
    created_at: datetime
    updated_at: datetime


class MenuItemListResponse(BaseModel):
    items: list[MenuItemResponse]
    total: int


# --- Modifier schemas ---


class CreateModifierGroupRequest(BaseModel):
    name: str = Field(..., max_length=255)
    description: str | None = None
    selection_type: str = "SINGLE"
    min_selections: int = Field(0, ge=0)
    max_selections: int = Field(1, ge=1)
    is_required: bool = False
    display_order: int = 0


class AddModifierRequest(BaseModel):
    name: str = Field(..., max_length=255)
    price_adjustment_amount: Decimal = Field(Decimal("0.00"), ge=0)
    price_adjustment_currency: str = "INR"
    is_default: bool = False
    display_order: int = 0


class ModifierResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    modifier_group_id: uuid.UUID
    name: str
    price_adjustment_amount: Decimal
    price_adjustment_currency: str
    is_default: bool
    is_available: bool
    display_order: int
    created_at: datetime
    updated_at: datetime


class ModifierGroupResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    menu_item_id: uuid.UUID
    restaurant_id: uuid.UUID
    name: str
    description: str | None
    selection_type: str
    min_selections: int
    max_selections: int
    is_required: bool
    display_order: int
    modifiers: list[ModifierResponse]
    created_at: datetime
    updated_at: datetime
