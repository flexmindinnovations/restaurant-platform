import uuid
from dataclasses import dataclass

from modules.reviews.application.ports.review_repository import ReviewRepository
from shared.application.ports.unit_of_work import AbstractUnitOfWork
from shared.domain.exceptions import NotFoundException, ValidationException


@dataclass(frozen=True)
class UpdateReviewCommand:
    review_id: uuid.UUID
    customer_id: uuid.UUID
    rating: int | None = None
    comment: str | None = None


class UpdateReviewHandler:
    def __init__(self, review_repo: ReviewRepository, uow: AbstractUnitOfWork) -> None:
        self._review_repo = review_repo
        self._uow = uow

    async def handle(self, command: UpdateReviewCommand) -> None:
        review = await self._review_repo.get_by_id(command.review_id)
        if not review:
            raise NotFoundException("Review not found")
        if review.customer_id != command.customer_id:
            raise ValidationException("You can only edit your own reviews")

        async with self._uow:
            review.update(rating=command.rating, comment=command.comment)
            await self._review_repo.update(review)
            self._uow.register_aggregate(review)
            await self._uow.commit()
