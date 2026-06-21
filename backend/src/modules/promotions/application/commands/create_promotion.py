import uuid
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from modules.promotions.application.ports.promotion_repository import PromotionRepository
from modules.promotions.domain.entities.promotion import Promotion
from modules.promotions.domain.value_objects.promotion_type import PromotionType
from shared.application.ports.unit_of_work import AbstractUnitOfWork
from shared.domain.exceptions import ValidationException
from shared.domain.value_objects import Money


@dataclass(frozen=True)
class CreatePromotionCommand:
    code: str
    description: str
    promotion_type: PromotionType
    value: Decimal
    valid_from: datetime
    valid_until: datetime
    min_order_amount: Decimal | None = None
    max_discount_amount: Decimal | None = None
    currency: str = "INR"
    max_total_uses: int | None = None
    max_uses_per_customer: int = 1
    restaurant_id: uuid.UUID | None = None


class CreatePromotionHandler:
    def __init__(self, promo_repo: PromotionRepository, uow: AbstractUnitOfWork) -> None:
        self._promo_repo = promo_repo
        self._uow = uow

    async def handle(self, command: CreatePromotionCommand) -> uuid.UUID:
        existing = await self._promo_repo.get_by_code(command.code.upper())
        if existing:
            raise ValidationException(f"Promotion code '{command.code.upper()}' already exists")

        min_order = (
            Money(amount=command.min_order_amount, currency=command.currency) if command.min_order_amount else None
        )
        max_disc = (
            Money(amount=command.max_discount_amount, currency=command.currency)
            if command.max_discount_amount
            else None
        )

        async with self._uow:
            promotion = Promotion.create(
                code=command.code,
                description=command.description,
                promotion_type=command.promotion_type,
                value=command.value,
                valid_from=command.valid_from,
                valid_until=command.valid_until,
                min_order_amount=min_order,
                max_discount=max_disc,
                max_total_uses=command.max_total_uses,
                max_uses_per_customer=command.max_uses_per_customer,
                restaurant_id=command.restaurant_id,
            )
            await self._promo_repo.add(promotion)
            self._uow.register_aggregate(promotion)
            await self._uow.commit()

        return promotion.id
