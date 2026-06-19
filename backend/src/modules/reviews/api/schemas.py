import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SubmitReviewRequest(BaseModel):
    restaurant_id: uuid.UUID
    rating: int = Field(..., ge=1, le=5)
    comment: str = Field("", max_length=2000)
    images: list[str] = Field(default_factory=list, max_length=5)


class UpdateReviewRequest(BaseModel):
    rating: int | None = Field(None, ge=1, le=5)
    comment: str | None = Field(None, max_length=2000)


class ReplyToReviewRequest(BaseModel):
    reply: str = Field(..., min_length=1, max_length=1000)


class FlagReviewRequest(BaseModel):
    reason: str = Field(..., min_length=1, max_length=500)


class ReviewResponse(BaseModel):
    id: uuid.UUID
    order_id: uuid.UUID
    customer_id: uuid.UUID
    restaurant_id: uuid.UUID
    rating: int
    comment: str
    sentiment: str | None
    is_flagged: bool
    flag_reason: str | None
    reply: str | None
    replied_at: datetime | None
    images: list[str]
    is_editable: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReviewListResponse(BaseModel):
    items: list[ReviewResponse]
    total: int


class ReviewSummaryResponse(BaseModel):
    restaurant_id: uuid.UUID
    average_rating: float
    total_reviews: int
    rating_distribution: dict[int, int]
    themes: list[str]

    model_config = ConfigDict(from_attributes=True)
