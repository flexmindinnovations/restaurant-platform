import uuid
from dataclasses import dataclass

from modules.promotions.application.ports.promotion_repository import PromotionRepository
from shared.application.ports.unit_of_work import AbstractUnitOfWork
from shared.domain.exceptions import NotFoundException


@dataclass(frozen=True)
class DeactivatePromotionCommand:
    promotion_id: uuid.UUID


class DeactivatePromotionHandler:
    def __init__(self, promo_repo: PromotionRepository, uow: AbstractUnitOfWork) -> None:
        self._promo_repo = promo_repo
        self._uow = uow

    async def handle(self, command: DeactivatePromotionCommand) -> None:
        promotion = await self._promo_repo.get_by_id(command.promotion_id)
        if not promotion:
            raise NotFoundException("Promotion not found")

        async with self._uow:
            promotion.deactivate()
            await self._promo_repo.update(promotion)
            self._uow.register_aggregate(promotion)
            await self._uow.commit()
