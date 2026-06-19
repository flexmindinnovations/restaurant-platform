import uuid

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.reviews.application.ports.review_repository import ReviewRepository
from modules.reviews.domain.entities.review import Review
from modules.reviews.domain.entities.review_summary import ReviewSummary
from modules.reviews.domain.value_objects.review_rating import ReviewRating
from modules.reviews.domain.value_objects.sentiment import Sentiment
from modules.reviews.infrastructure.models.review_models import ReviewModel


class SqlAlchemyReviewRepository(ReviewRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, review: Review) -> None:
        model = ReviewModel(
            id=review.id,
            order_id=review.order_id,
            customer_id=review.customer_id,
            restaurant_id=review.restaurant_id,
            rating=review.rating.value,
            comment=review.comment,
            sentiment=review.sentiment.value if review.sentiment else None,
            is_flagged=review.is_flagged,
            flag_reason=review.flag_reason,
            reply=review.reply,
            replied_at=review.replied_at,
            images=review.images,
            created_at=review.created_at,
            updated_at=review.updated_at,
        )
        self._session.add(model)

    async def get_by_id(self, review_id: uuid.UUID) -> Review | None:
        result = await self._session.execute(select(ReviewModel).where(ReviewModel.id == review_id))
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def get_by_order_id(self, order_id: uuid.UUID) -> Review | None:
        result = await self._session.execute(select(ReviewModel).where(ReviewModel.order_id == order_id))
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def update(self, review: Review) -> None:
        result = await self._session.execute(select(ReviewModel).where(ReviewModel.id == review.id))
        model = result.scalar_one_or_none()
        if model:
            model.rating = review.rating.value
            model.comment = review.comment
            model.sentiment = review.sentiment.value if review.sentiment else None
            model.is_flagged = review.is_flagged
            model.flag_reason = review.flag_reason
            model.reply = review.reply
            model.replied_at = review.replied_at
            model.images = review.images
            model.updated_at = review.updated_at

    async def list_by_restaurant(
        self, restaurant_id: uuid.UUID, skip: int = 0, limit: int = 10
    ) -> tuple[list[Review], int]:
        base_query = select(ReviewModel).where(ReviewModel.restaurant_id == restaurant_id)
        count_query = select(func.count()).select_from(base_query.subquery())
        total = await self._session.scalar(count_query) or 0

        result = await self._session.execute(
            base_query.order_by(ReviewModel.created_at.desc()).offset(skip).limit(limit)
        )
        models = result.scalars().all()
        return [self._to_domain(m) for m in models], total

    async def list_by_customer(
        self, customer_id: uuid.UUID, skip: int = 0, limit: int = 10
    ) -> tuple[list[Review], int]:
        base_query = select(ReviewModel).where(ReviewModel.customer_id == customer_id)
        count_query = select(func.count()).select_from(base_query.subquery())
        total = await self._session.scalar(count_query) or 0

        result = await self._session.execute(
            base_query.order_by(ReviewModel.created_at.desc()).offset(skip).limit(limit)
        )
        models = result.scalars().all()
        return [self._to_domain(m) for m in models], total

    async def list_flagged(self, skip: int = 0, limit: int = 10) -> tuple[list[Review], int]:
        base_query = select(ReviewModel).where(ReviewModel.is_flagged.is_(True))
        count_query = select(func.count()).select_from(base_query.subquery())
        total = await self._session.scalar(count_query) or 0

        result = await self._session.execute(
            base_query.order_by(ReviewModel.created_at.desc()).offset(skip).limit(limit)
        )
        models = result.scalars().all()
        return [self._to_domain(m) for m in models], total

    async def get_summary(self, restaurant_id: uuid.UUID) -> ReviewSummary:
        base = select(ReviewModel).where(ReviewModel.restaurant_id == restaurant_id)

        avg_result = await self._session.scalar(
            select(func.avg(ReviewModel.rating)).where(ReviewModel.restaurant_id == restaurant_id)
        )
        count_result = await self._session.scalar(select(func.count()).select_from(base.subquery()))

        distribution: dict[int, int] = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        dist_query = (
            select(ReviewModel.rating, func.count().label("cnt"))
            .where(ReviewModel.restaurant_id == restaurant_id)
            .group_by(ReviewModel.rating)
        )
        dist_result = await self._session.execute(dist_query)
        for row in dist_result:
            distribution[row.rating] = row.cnt

        sentiment_query = (
            select(
                ReviewModel.sentiment,
                func.count(case((ReviewModel.sentiment == "POSITIVE", 1))).label("pos"),
                func.count(case((ReviewModel.sentiment == "NEGATIVE", 1))).label("neg"),
            )
            .where(ReviewModel.restaurant_id == restaurant_id)
            .where(ReviewModel.sentiment.isnot(None))
            .group_by(ReviewModel.sentiment)
        )
        await self._session.execute(sentiment_query)

        return ReviewSummary(
            restaurant_id=restaurant_id,
            average_rating=round(float(avg_result or 0), 2),
            total_reviews=count_result or 0,
            rating_distribution=distribution,
        )

    def _to_domain(self, model: ReviewModel) -> Review:
        return Review(
            id=model.id,
            order_id=model.order_id,
            customer_id=model.customer_id,
            restaurant_id=model.restaurant_id,
            rating=ReviewRating(value=model.rating),
            comment=model.comment,
            sentiment=Sentiment(model.sentiment) if model.sentiment else None,
            is_flagged=model.is_flagged,
            flag_reason=model.flag_reason,
            reply=model.reply,
            replied_at=model.replied_at,
            images=list(model.images) if model.images else [],
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
