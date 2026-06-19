import uuid
from dataclasses import dataclass

from modules.reviews.application.ports.review_repository import ReviewRepository
from modules.reviews.domain.entities.review_summary import ReviewSummary


@dataclass(frozen=True)
class GetReviewSummaryQuery:
    restaurant_id: uuid.UUID


class GetReviewSummaryHandler:
    def __init__(self, review_repo: ReviewRepository) -> None:
        self._review_repo = review_repo

    async def handle(self, query: GetReviewSummaryQuery) -> ReviewSummary:
        return await self._review_repo.get_summary(query.restaurant_id)
