import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal

from modules.promotions.domain.events.promotion_events import CouponApplied, PromotionCreated, PromotionDeactivated
from modules.promotions.domain.value_objects.promotion_status import PromotionStatus
from modules.promotions.domain.value_objects.promotion_type import PromotionType
from shared.domain.entity import AggregateRoot
from shared.domain.exceptions import ValidationException
from shared.domain.value_objects import Money

MAX_CODE_LENGTH = 50
MAX_DESCRIPTION_LENGTH = 500


@dataclass
class Promotion(AggregateRoot):
    code: str = ""
    description: str = ""
    promotion_type: PromotionType = PromotionType.PERCENTAGE
    value: Decimal = Decimal("0")
    min_order_amount: Money | None = None
    max_discount: Money | None = None
    valid_from: datetime = None  # type: ignore[assignment]
    valid_until: datetime = None  # type: ignore[assignment]
    max_total_uses: int | None = None
    max_uses_per_customer: int = 1
    total_uses: int = 0
    status: PromotionStatus = PromotionStatus.ACTIVE
    restaurant_id: uuid.UUID | None = None

    @classmethod
    def create(
        cls,
        code: str,
        description: str,
        promotion_type: PromotionType,
        value: Decimal,
        valid_from: datetime,
        valid_until: datetime,
        min_order_amount: Money | None = None,
        max_discount: Money | None = None,
        max_total_uses: int | None = None,
        max_uses_per_customer: int = 1,
        restaurant_id: uuid.UUID | None = None,
    ) -> "Promotion":
        if not code or len(code) > MAX_CODE_LENGTH:
            raise ValidationException(f"Promotion code must be 1-{MAX_CODE_LENGTH} characters")
        if value <= 0:
            raise ValidationException("Promotion value must be positive")
        if valid_until <= valid_from:
            raise ValidationException("valid_until must be after valid_from")
        if promotion_type == PromotionType.PERCENTAGE and value > Decimal("100"):
            raise ValidationException("Percentage discount cannot exceed 100%")

        now = datetime.now(UTC)
        promo_id = uuid.uuid4()

        promo = cls(
            id=promo_id,
            code=code.upper(),
            description=description,
            promotion_type=promotion_type,
            value=value,
            min_order_amount=min_order_amount,
            max_discount=max_discount,
            valid_from=valid_from,
            valid_until=valid_until,
            max_total_uses=max_total_uses,
            max_uses_per_customer=max_uses_per_customer,
            restaurant_id=restaurant_id,
            created_at=now,
            updated_at=now,
        )

        promo.register_event(
            PromotionCreated(
                aggregate_id=promo_id,
                code=code.upper(),
                promotion_type=promotion_type.value,
            )
        )
        return promo

    @property
    def is_valid(self) -> bool:
        now = datetime.now(UTC)
        if self.status != PromotionStatus.ACTIVE:
            return False
        if now < self.valid_from or now > self.valid_until:
            return False
        return not (self.max_total_uses is not None and self.total_uses >= self.max_total_uses)

    def validate_for_order(self, order_amount: Money, customer_usage_count: int) -> None:
        if not self.is_valid:
            raise ValidationException("This promotion is no longer valid")
        if self.min_order_amount and order_amount.amount < self.min_order_amount.amount:
            raise ValidationException(
                f"Minimum order amount of {self.min_order_amount.amount} {self.min_order_amount.currency} required"
            )
        if customer_usage_count >= self.max_uses_per_customer:
            raise ValidationException("You have already used this promotion the maximum number of times")

    def calculate_discount(self, order_amount: Money) -> Money:
        currency = order_amount.currency

        if self.promotion_type == PromotionType.PERCENTAGE:
            discount = (order_amount.amount * self.value / Decimal("100")).quantize(Decimal("0.01"))
        elif self.promotion_type == PromotionType.FIXED_AMOUNT:
            discount = min(self.value, order_amount.amount)
        elif self.promotion_type == PromotionType.FREE_DELIVERY:
            return Money(amount=Decimal("0"), currency=currency)
        else:
            discount = Decimal("0")

        if self.max_discount:
            discount = min(discount, self.max_discount.amount)

        return Money(amount=discount, currency=currency)

    def apply(self, order_id: uuid.UUID, customer_id: uuid.UUID, discount_amount: Decimal) -> None:
        self.total_uses += 1
        self.updated_at = datetime.now(UTC)
        self.register_event(
            CouponApplied(
                aggregate_id=self.id,
                order_id=order_id,
                customer_id=customer_id,
                discount_amount=discount_amount,
            )
        )

    def deactivate(self) -> None:
        self.status = PromotionStatus.INACTIVE
        self.updated_at = datetime.now(UTC)
        self.register_event(PromotionDeactivated(aggregate_id=self.id))
