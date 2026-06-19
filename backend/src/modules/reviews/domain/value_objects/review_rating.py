from dataclasses import dataclass

from shared.domain.exceptions import ValidationException

MIN_RATING = 1
MAX_RATING = 5


@dataclass(frozen=True)
class ReviewRating:
    value: int

    def __post_init__(self) -> None:
        if not MIN_RATING <= self.value <= MAX_RATING:
            raise ValidationException(f"Rating must be between {MIN_RATING} and {MAX_RATING}")
