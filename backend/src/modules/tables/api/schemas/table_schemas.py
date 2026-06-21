import uuid
import datetime as _dt
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Section schemas
# ---------------------------------------------------------------------------


class CreateSectionRequest(BaseModel):
    name: str = Field(..., max_length=100)
    description: str | None = None
    display_order: int = 0


class UpdateSectionRequest(BaseModel):
    name: str | None = Field(None, max_length=100)
    description: str | None = None
    display_order: int | None = None


class SectionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    restaurant_id: uuid.UUID
    name: str
    description: str | None
    display_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Table schemas
# ---------------------------------------------------------------------------


class CreateTableRequest(BaseModel):
    number: str = Field(..., max_length=20)
    section_id: uuid.UUID | None = None
    capacity_min: int = Field(1, ge=1)
    capacity_max: int = Field(..., ge=1)
    shape: str = "RECTANGULAR"
    position_x: int = 0
    position_y: int = 0
    turn_time_minutes: int = Field(90, ge=1)
    buffer_minutes: int = Field(15, ge=0)


class UpdateTableRequest(BaseModel):
    number: str | None = Field(None, max_length=20)
    section_id: uuid.UUID | None = None
    capacity_min: int | None = Field(None, ge=1)
    capacity_max: int | None = Field(None, ge=1)
    shape: str | None = None
    position_x: int | None = None
    position_y: int | None = None
    turn_time_minutes: int | None = Field(None, ge=1)
    buffer_minutes: int | None = Field(None, ge=0)


class UpdateTableStatusRequest(BaseModel):
    status: str


class TableResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    restaurant_id: uuid.UUID
    section_id: uuid.UUID | None
    number: str
    capacity_min: int
    capacity_max: int
    shape: str
    position_x: int
    position_y: int
    status: str
    turn_time_minutes: int
    buffer_minutes: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Reservation schemas
# ---------------------------------------------------------------------------


class CreateReservationRequest(BaseModel):
    restaurant_id: uuid.UUID
    date: _dt.date
    start_time: _dt.time
    party_size: int = Field(..., ge=1)
    customer_name: str = Field(..., max_length=255)
    customer_phone: str | None = Field(None, max_length=20)
    customer_email: str | None = Field(None, max_length=255)
    special_requests: str | None = None
    table_id: uuid.UUID | None = None
    source: str = "PLATFORM"


class UpdateReservationRequest(BaseModel):
    date: _dt.date | None = None
    start_time: _dt.time | None = None
    party_size: int | None = Field(None, ge=1)
    table_id: uuid.UUID | None = None
    special_requests: str | None = None


class ConfirmReservationRequest(BaseModel):
    table_id: uuid.UUID


class CancelReservationRequest(BaseModel):
    reason: str | None = None


class ReservationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    restaurant_id: uuid.UUID
    table_id: uuid.UUID | None
    customer_id: uuid.UUID | None
    customer_name: str
    customer_phone: str | None
    customer_email: str | None
    date: _dt.date
    start_time: _dt.time
    end_time: _dt.time
    party_size: int
    status: str
    special_requests: str | None
    internal_notes: str | None
    source: str
    seated_at: datetime | None
    completed_at: datetime | None
    cancelled_at: datetime | None
    cancellation_reason: str | None
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Waitlist schemas
# ---------------------------------------------------------------------------


class JoinWaitlistRequest(BaseModel):
    restaurant_id: uuid.UUID
    customer_name: str = Field(..., max_length=255)
    customer_phone: str = Field(..., max_length=20)
    party_size: int = Field(..., ge=1)
    preferred_section: uuid.UUID | None = None
    special_requests: str | None = None


class WaitlistEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    restaurant_id: uuid.UUID
    customer_name: str
    customer_phone: str
    customer_id: uuid.UUID | None
    party_size: int
    estimated_wait_minutes: int
    queue_position: int
    status: str
    preferred_section: uuid.UUID | None
    special_requests: str | None
    notified_at: datetime | None
    seated_at: datetime | None
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Floor plan & availability
# ---------------------------------------------------------------------------


class FloorPlanSectionResponse(BaseModel):
    section: SectionResponse
    tables: list[TableResponse]


class FloorPlanResponse(BaseModel):
    sections: list[FloorPlanSectionResponse]
    unassigned_tables: list[TableResponse]


class AvailableSlotResponse(BaseModel):
    start_time: _dt.time
    end_time: _dt.time
    table_id: uuid.UUID
    table_number: str
    capacity_min: int
    capacity_max: int


class AvailableSlotsResponse(BaseModel):
    slots: list[AvailableSlotResponse]


# ---------------------------------------------------------------------------
# List response wrappers
# ---------------------------------------------------------------------------


class SectionListResponse(BaseModel):
    items: list[SectionResponse]
    total: int


class TableListResponse(BaseModel):
    items: list[TableResponse]
    total: int


class ReservationListResponse(BaseModel):
    items: list[ReservationResponse]
    total: int


class WaitlistListResponse(BaseModel):
    items: list[WaitlistEntryResponse]
    total: int
