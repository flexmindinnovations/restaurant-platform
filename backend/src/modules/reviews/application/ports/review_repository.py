import abc
import uuid

from modules.reviews.domain.entities.review import Review
from modules.reviews.domain.entities.review_summary import ReviewSummary


class ReviewRepository(abc.ABC):
    @abc.abstractmethod
    async def add(self, review: Review) -> None:
        pass

    @abc.abstractmethod
    async def get_by_id(self, review_id: uuid.UUID) -> Review | None:
        pass

    @abc.abstractmethod
    async def get_by_order_id(self, order_id: uuid.UUID) -> Review | None:
        pass

    @abc.abstractmethod
    async def update(self, review: Review) -> None:
        pass

    @abc.abstractmethod
    async def list_by_restaurant(
        self, restaurant_id: uuid.UUID, skip: int = 0, limit: int = 10
    ) -> tuple[list[Review], int]:
        pass

    @abc.abstractmethod
    async def list_by_customer(
        self, customer_id: uuid.UUID, skip: int = 0, limit: int = 10
    ) -> tuple[list[Review], int]:
        pass

    @abc.abstractmethod
    async def list_flagged(self, skip: int = 0, limit: int = 10) -> tuple[list[Review], int]:
        pass

    @abc.abstractmethod
    async def get_summary(self, restaurant_id: uuid.UUID) -> ReviewSummary:
        pass
