import uuid
from dataclasses import dataclass
from decimal import Decimal

from modules.promotions.application.ports.promotion_repository import PromotionRepository
from modules.promotions.domain.entities.coupon_usage import CouponUsage
from shared.application.ports.unit_of_work import AbstractUnitOfWork
from shared.domain.exceptions import NotFoundException
from shared.domain.value_objects import Money


@dataclass(frozen=True)
class ApplyPromotionCommand:
    code: str
    order_id: uuid.UUID
    customer_id: uuid.UUID
    order_amount: Decimal
    currency: str = "INR"


@dataclass(frozen=True)
class ApplyPromotionResult:
    promotion_id: uuid.UUID
    discount_amount: Decimal
    discount_currency: str


class ApplyPromotionHandler:
    def __init__(self, promo_repo: PromotionRepository, uow: AbstractUnitOfWork) -> None:
        self._promo_repo = promo_repo
        self._uow = uow

    async def handle(self, command: ApplyPromotionCommand) -> ApplyPromotionResult:
        promotion = await self._promo_repo.get_by_code(command.code.upper())
        if not promotion:
            raise NotFoundException("Promotion not found")

        customer_usage = await self._promo_repo.count_customer_usage(promotion.id, command.customer_id)
        order_money = Money(amount=command.order_amount, currency=command.currency)

        promotion.validate_for_order(order_money, customer_usage)
        discount = promotion.calculate_discount(order_money)

        async with self._uow:
            promotion.apply(command.order_id, command.customer_id, discount.amount)
            await self._promo_repo.update(promotion)

            usage = CouponUsage.record(
                promotion_id=promotion.id,
                order_id=command.order_id,
                customer_id=command.customer_id,
                discount_amount=discount.amount,
                discount_currency=discount.currency,
            )
            await self._promo_repo.add_usage(usage)
            self._uow.register_aggregate(promotion)
            await self._uow.commit()

        return ApplyPromotionResult(
            promotion_id=promotion.id,
            discount_amount=discount.amount,
            discount_currency=discount.currency,
        )
