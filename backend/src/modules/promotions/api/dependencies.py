from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db_session
from modules.promotions.application.commands.apply_promotion import ApplyPromotionHandler
from modules.promotions.application.commands.create_promotion import CreatePromotionHandler
from modules.promotions.application.commands.deactivate_promotion import DeactivatePromotionHandler
from modules.promotions.application.ports.promotion_repository import PromotionRepository
from modules.promotions.application.queries.list_promotions import ListPromotionsHandler
from modules.promotions.application.queries.validate_promotion import ValidatePromotionHandler
from modules.promotions.infrastructure.repositories.sqlalchemy_promotion_repository import (
    SqlAlchemyPromotionRepository,
)
from shared.application.ports.unit_of_work import AbstractUnitOfWork
from shared.infrastructure.event_bus import get_event_bus
from shared.infrastructure.unit_of_work import SqlAlchemyUnitOfWork


def _promo_repo(session: AsyncSession = Depends(get_db_session)) -> PromotionRepository:
    return SqlAlchemyPromotionRepository(session)


def _uow(session: AsyncSession = Depends(get_db_session)) -> AbstractUnitOfWork:
    return SqlAlchemyUnitOfWork(session, get_event_bus())


def get_create_promotion_handler(
    promo_repo: PromotionRepository = Depends(_promo_repo),
    uow: AbstractUnitOfWork = Depends(_uow),
) -> CreatePromotionHandler:
    return CreatePromotionHandler(promo_repo, uow)


def get_apply_promotion_handler(
    promo_repo: PromotionRepository = Depends(_promo_repo),
    uow: AbstractUnitOfWork = Depends(_uow),
) -> ApplyPromotionHandler:
    return ApplyPromotionHandler(promo_repo, uow)


def get_deactivate_promotion_handler(
    promo_repo: PromotionRepository = Depends(_promo_repo),
    uow: AbstractUnitOfWork = Depends(_uow),
) -> DeactivatePromotionHandler:
    return DeactivatePromotionHandler(promo_repo, uow)


def get_list_promotions_handler(
    promo_repo: PromotionRepository = Depends(_promo_repo),
) -> ListPromotionsHandler:
    return ListPromotionsHandler(promo_repo)


def get_validate_promotion_handler(
    promo_repo: PromotionRepository = Depends(_promo_repo),
) -> ValidatePromotionHandler:
    return ValidatePromotionHandler(promo_repo)
