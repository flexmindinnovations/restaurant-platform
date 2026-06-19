import pathlib
import sys
from typing import Any

import structlog
from sqlalchemy import select

from modules.reviews.infrastructure.models.review_models import ReviewModel
from shared.infrastructure.database import get_session_factory
from shared.infrastructure.event_bus import InMemoryEventBus

# Ensure the AI module can be loaded
ai_path = str((pathlib.Path(__file__).parent / "../../../../ai/src").resolve())
if ai_path not in sys.path:
    sys.path.append(ai_path)

from models.sentiment_classifier import SentimentClassifier  # noqa: E402

logger = structlog.get_logger()


async def handle_review_submitted(event: Any) -> None:
    review_id = event.aggregate_id
    session_factory = get_session_factory()
    classifier = SentimentClassifier()

    async with session_factory() as session:
        stmt = select(ReviewModel).where(ReviewModel.id == review_id)
        result = await session.execute(stmt)
        review = result.scalar_one_or_none()

        if not review:
            logger.error("Review not found for sentiment analysis", review_id=str(review_id))
            return

        if not review.comment or not review.comment.strip():
            review.sentiment = "NEUTRAL"
        else:
            try:
                sentiment = await classifier.classify(review.comment)
                review.sentiment = sentiment
            except Exception as e:
                logger.exception("Failed to analyze sentiment for review", review_id=str(review_id), error=str(e))
                review.sentiment = "NEUTRAL"

        await session.commit()
        logger.info(
            "Successfully analyzed and updated review sentiment", review_id=str(review_id), sentiment=review.sentiment
        )


def register_event_handlers(event_bus: InMemoryEventBus) -> None:
    event_bus.subscribe_by_name("ReviewSubmitted", handle_review_submitted)
