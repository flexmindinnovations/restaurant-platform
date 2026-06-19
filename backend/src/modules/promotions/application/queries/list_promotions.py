from dataclasses import dataclass

from modules.promotions.application.ports.promotion_repository import PromotionRepository
from modules.promotions.domain.entities.promotion import Promotion


@dataclass(frozen=True)
class ListPromotionsQuery:
    available_only: bool = False
    skip: int = 0
    limit: int = 10


class ListPromotionsHandler:
    def __init__(self, promo_repo: PromotionRepository) -> None:
        self._promo_repo = promo_repo

    async def handle(self, query: ListPromotionsQuery) -> tuple[list[Promotion], int]:
        if query.available_only:
            return await self._promo_repo.list_available(skip=query.skip, limit=query.limit)
        return await self._promo_repo.list_all(skip=query.skip, limit=query.limit)
