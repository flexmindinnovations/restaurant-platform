import uuid
from dataclasses import dataclass, field

from modules.reviews.application.ports.review_repository import ReviewRepository
from modules.reviews.domain.entities.review import Review
from shared.application.ports.unit_of_work import AbstractUnitOfWork
from shared.domain.exceptions import ValidationException


@dataclass(frozen=True)
class SubmitReviewCommand:
    order_id: uuid.UUID
    customer_id: uuid.UUID
    restaurant_id: uuid.UUID
    rating: int
    comment: str = ""
    images: list[str] = field(default_factory=list)


class SubmitReviewHandler:
    def __init__(self, review_repo: ReviewRepository, uow: AbstractUnitOfWork) -> None:
        self._review_repo = review_repo
        self._uow = uow

    async def handle(self, command: SubmitReviewCommand) -> uuid.UUID:
        existing = await self._review_repo.get_by_order_id(command.order_id)
        if existing:
            raise ValidationException("A review already exists for this order")

        async with self._uow:
            review = Review.submit(
                order_id=command.order_id,
                customer_id=command.customer_id,
                restaurant_id=command.restaurant_id,
                rating=command.rating,
                comment=command.comment,
                images=command.images,
            )
            await self._review_repo.add(review)
            self._uow.register_aggregate(review)
            await self._uow.commit()

        return review.id
