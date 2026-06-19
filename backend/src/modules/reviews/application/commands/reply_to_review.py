import uuid
from dataclasses import dataclass

from modules.reviews.application.ports.review_repository import ReviewRepository
from shared.application.ports.unit_of_work import AbstractUnitOfWork
from shared.domain.exceptions import NotFoundException


@dataclass(frozen=True)
class ReplyToReviewCommand:
    review_id: uuid.UUID
    reply: str


class ReplyToReviewHandler:
    def __init__(self, review_repo: ReviewRepository, uow: AbstractUnitOfWork) -> None:
        self._review_repo = review_repo
        self._uow = uow

    async def handle(self, command: ReplyToReviewCommand) -> None:
        review = await self._review_repo.get_by_id(command.review_id)
        if not review:
            raise NotFoundException("Review not found")

        async with self._uow:
            review.add_reply(command.reply)
            await self._review_repo.update(review)
            self._uow.register_aggregate(review)
            await self._uow.commit()
