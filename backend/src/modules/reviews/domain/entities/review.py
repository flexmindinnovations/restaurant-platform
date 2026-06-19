import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

from modules.reviews.domain.events.review_events import (
    ReviewFlagged,
    ReviewReplied,
    ReviewSubmitted,
    ReviewUpdated,
)
from modules.reviews.domain.value_objects.review_rating import ReviewRating
from modules.reviews.domain.value_objects.sentiment import Sentiment
from shared.domain.entity import AggregateRoot
from shared.domain.exceptions import ValidationException

EDIT_WINDOW_HOURS = 48
MAX_COMMENT_LENGTH = 2000
MAX_REPLY_LENGTH = 1000
MAX_IMAGES = 5


@dataclass
class Review(AggregateRoot):
    order_id: uuid.UUID = None  # type: ignore[assignment]
    customer_id: uuid.UUID = None  # type: ignore[assignment]
    restaurant_id: uuid.UUID = None  # type: ignore[assignment]
    rating: ReviewRating = None  # type: ignore[assignment]
    comment: str = ""
    sentiment: Sentiment | None = None
    is_flagged: bool = False
    flag_reason: str | None = None
    reply: str | None = None
    replied_at: datetime | None = None
    images: list[str] = field(default_factory=list)

    @classmethod
    def submit(
        cls,
        order_id: uuid.UUID,
        customer_id: uuid.UUID,
        restaurant_id: uuid.UUID,
        rating: int,
        comment: str = "",
        images: list[str] | None = None,
    ) -> "Review":
        review_rating = ReviewRating(value=rating)
        if len(comment) > MAX_COMMENT_LENGTH:
            raise ValidationException(f"Comment must be {MAX_COMMENT_LENGTH} characters or fewer")
        if images and len(images) > MAX_IMAGES:
            raise ValidationException(f"Maximum {MAX_IMAGES} images allowed per review")

        now = datetime.now(UTC)
        review_id = uuid.uuid4()

        review = cls(
            id=review_id,
            order_id=order_id,
            customer_id=customer_id,
            restaurant_id=restaurant_id,
            rating=review_rating,
            comment=comment,
            images=images or [],
            created_at=now,
            updated_at=now,
        )

        review.register_event(
            ReviewSubmitted(
                aggregate_id=review_id,
                order_id=order_id,
                restaurant_id=restaurant_id,
                customer_id=customer_id,
                rating=rating,
            )
        )
        return review

    def update(self, rating: int | None = None, comment: str | None = None) -> None:
        elapsed = datetime.now(UTC) - self.created_at
        if elapsed > timedelta(hours=EDIT_WINDOW_HOURS):
            raise ValidationException(f"Reviews can only be edited within {EDIT_WINDOW_HOURS} hours of submission")

        if rating is not None:
            self.rating = ReviewRating(value=rating)
        if comment is not None:
            if len(comment) > MAX_COMMENT_LENGTH:
                raise ValidationException(f"Comment must be {MAX_COMMENT_LENGTH} characters or fewer")
            self.comment = comment

        self.updated_at = datetime.now(UTC)
        self.register_event(ReviewUpdated(aggregate_id=self.id, rating=self.rating.value))

    def add_reply(self, reply_text: str) -> None:
        if not reply_text or not reply_text.strip():
            raise ValidationException("Reply cannot be empty")
        if len(reply_text) > MAX_REPLY_LENGTH:
            raise ValidationException(f"Reply must be {MAX_REPLY_LENGTH} characters or fewer")

        self.reply = reply_text
        self.replied_at = datetime.now(UTC)
        self.updated_at = datetime.now(UTC)
        self.register_event(ReviewReplied(aggregate_id=self.id, restaurant_id=self.restaurant_id))

    def flag(self, reason: str) -> None:
        if not reason or not reason.strip():
            raise ValidationException("Flag reason is required")
        self.is_flagged = True
        self.flag_reason = reason
        self.updated_at = datetime.now(UTC)
        self.register_event(ReviewFlagged(aggregate_id=self.id, reason=reason))

    def unflag(self) -> None:
        self.is_flagged = False
        self.flag_reason = None
        self.updated_at = datetime.now(UTC)

    @property
    def is_editable(self) -> bool:
        elapsed = datetime.now(UTC) - self.created_at
        return elapsed <= timedelta(hours=EDIT_WINDOW_HOURS)
