from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db_session
from modules.reviews.application.commands.flag_review import FlagReviewHandler
from modules.reviews.application.commands.reply_to_review import ReplyToReviewHandler
from modules.reviews.application.commands.submit_review import SubmitReviewHandler
from modules.reviews.application.commands.update_review import UpdateReviewHandler
from modules.reviews.application.ports.review_repository import ReviewRepository
from modules.reviews.application.queries.get_review import GetReviewHandler
from modules.reviews.application.queries.get_review_summary import GetReviewSummaryHandler
from modules.reviews.application.queries.list_restaurant_reviews import ListRestaurantReviewsHandler
from modules.reviews.infrastructure.repositories.sqlalchemy_review_repository import SqlAlchemyReviewRepository
from shared.application.ports.unit_of_work import AbstractUnitOfWork
from shared.infrastructure.event_bus import get_event_bus
from shared.infrastructure.unit_of_work import SqlAlchemyUnitOfWork


def _review_repo(session: AsyncSession = Depends(get_db_session)) -> ReviewRepository:
    return SqlAlchemyReviewRepository(session)


def _uow(session: AsyncSession = Depends(get_db_session)) -> AbstractUnitOfWork:
    return SqlAlchemyUnitOfWork(session, get_event_bus())


def get_submit_review_handler(
    review_repo: ReviewRepository = Depends(_review_repo),
    uow: AbstractUnitOfWork = Depends(_uow),
) -> SubmitReviewHandler:
    return SubmitReviewHandler(review_repo, uow)


def get_update_review_handler(
    review_repo: ReviewRepository = Depends(_review_repo),
    uow: AbstractUnitOfWork = Depends(_uow),
) -> UpdateReviewHandler:
    return UpdateReviewHandler(review_repo, uow)


def get_reply_to_review_handler(
    review_repo: ReviewRepository = Depends(_review_repo),
    uow: AbstractUnitOfWork = Depends(_uow),
) -> ReplyToReviewHandler:
    return ReplyToReviewHandler(review_repo, uow)


def get_flag_review_handler(
    review_repo: ReviewRepository = Depends(_review_repo),
    uow: AbstractUnitOfWork = Depends(_uow),
) -> FlagReviewHandler:
    return FlagReviewHandler(review_repo, uow)


def get_review_query_handler(
    review_repo: ReviewRepository = Depends(_review_repo),
) -> GetReviewHandler:
    return GetReviewHandler(review_repo)


def get_list_restaurant_reviews_handler(
    review_repo: ReviewRepository = Depends(_review_repo),
) -> ListRestaurantReviewsHandler:
    return ListRestaurantReviewsHandler(review_repo)


def get_review_summary_handler(
    review_repo: ReviewRepository = Depends(_review_repo),
) -> GetReviewSummaryHandler:
    return GetReviewSummaryHandler(review_repo)
