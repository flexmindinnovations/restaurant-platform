import uuid
from dataclasses import dataclass

from modules.reviews.application.ports.review_repository import ReviewRepository
from modules.reviews.domain.entities.review import Review
from shared.domain.exceptions import NotFoundException


@dataclass(frozen=True)
class GetReviewQuery:
    review_id: uuid.UUID


class GetReviewHandler:
    def __init__(self, review_repo: ReviewRepository) -> None:
        self._review_repo = review_repo

    async def handle(self, query: GetReviewQuery) -> Review:
        review = await self._review_repo.get_by_id(query.review_id)
        if not review:
            raise NotFoundException("Review not found")
        return review
