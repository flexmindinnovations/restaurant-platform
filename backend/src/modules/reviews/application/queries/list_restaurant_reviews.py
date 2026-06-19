import uuid
from dataclasses import dataclass

from modules.reviews.application.ports.review_repository import ReviewRepository
from modules.reviews.domain.entities.review import Review


@dataclass(frozen=True)
class ListRestaurantReviewsQuery:
    restaurant_id: uuid.UUID
    skip: int = 0
    limit: int = 10


class ListRestaurantReviewsHandler:
    def __init__(self, review_repo: ReviewRepository) -> None:
        self._review_repo = review_repo

    async def handle(self, query: ListRestaurantReviewsQuery) -> tuple[list[Review], int]:
        return await self._review_repo.list_by_restaurant(
            restaurant_id=query.restaurant_id,
            skip=query.skip,
            limit=query.limit,
        )
