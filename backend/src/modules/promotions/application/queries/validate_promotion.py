from dataclasses import dataclass
from decimal import Decimal

from modules.promotions.application.ports.promotion_repository import PromotionRepository
from shared.domain.exceptions import NotFoundException
from shared.domain.value_objects import Money


@dataclass(frozen=True)
class ValidatePromotionQuery:
    code: str
    order_amount: Decimal
    currency: str = "INR"


@dataclass(frozen=True)
class ValidatePromotionResult:
    is_valid: bool
    discount_amount: Decimal
    discount_currency: str
    promotion_type: str
    description: str


class ValidatePromotionHandler:
    def __init__(self, promo_repo: PromotionRepository) -> None:
        self._promo_repo = promo_repo

    async def handle(self, query: ValidatePromotionQuery) -> ValidatePromotionResult:
        promotion = await self._promo_repo.get_by_code(query.code.upper())
        if not promotion:
            raise NotFoundException("Promotion not found")

        if not promotion.is_valid:
            return ValidatePromotionResult(
                is_valid=False,
                discount_amount=Decimal("0"),
                discount_currency=query.currency,
                promotion_type=promotion.promotion_type.value,
                description=promotion.description,
            )

        order_money = Money(amount=query.order_amount, currency=query.currency)
        discount = promotion.calculate_discount(order_money)

        return ValidatePromotionResult(
            is_valid=True,
            discount_amount=discount.amount,
            discount_currency=discount.currency,
            promotion_type=promotion.promotion_type.value,
            description=promotion.description,
        )
