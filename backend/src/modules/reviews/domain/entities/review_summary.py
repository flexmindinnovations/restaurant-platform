import uuid
from dataclasses import dataclass, field


@dataclass
class ReviewSummary:
    restaurant_id: uuid.UUID
    average_rating: float = 0.0
    total_reviews: int = 0
    rating_distribution: dict[int, int] = field(default_factory=lambda: {1: 0, 2: 0, 3: 0, 4: 0, 5: 0})
    themes: list[str] = field(default_factory=list)
