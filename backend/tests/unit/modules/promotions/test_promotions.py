import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from modules.promotions.application.commands.apply_promotion import ApplyPromotionCommand, ApplyPromotionHandler
from modules.promotions.application.commands.create_promotion import CreatePromotionCommand, CreatePromotionHandler
from modules.promotions.application.commands.deactivate_promotion import (
    DeactivatePromotionCommand,
    DeactivatePromotionHandler,
)
from modules.promotions.domain.entities.coupon_usage import CouponUsage
from modules.promotions.domain.entities.promotion import Promotion
from modules.promotions.domain.value_objects.promotion_status import PromotionStatus
from modules.promotions.domain.value_objects.promotion_type import PromotionType
from shared.domain.exceptions import NotFoundException, ValidationException
from shared.domain.value_objects import Money

# --- Helpers ---

NOW = datetime.now(UTC)
FUTURE = NOW + timedelta(days=30)
PAST = NOW - timedelta(days=30)


def _make_promotion(**kwargs) -> Promotion:
    defaults = {
        "code": "SAVE20",
        "description": "20% off",
        "promotion_type": PromotionType.PERCENTAGE,
        "value": Decimal("20"),
        "valid_from": NOW - timedelta(days=1),
        "valid_until": FUTURE,
    }
    defaults.update(kwargs)
    return Promotion.create(**defaults)


# --- Domain: PromotionType ---


@pytest.mark.unit
def test_promotion_type_values():
    assert PromotionType.PERCENTAGE == "PERCENTAGE"
    assert PromotionType.FIXED_AMOUNT == "FIXED_AMOUNT"
    assert PromotionType.FREE_DELIVERY == "FREE_DELIVERY"
    assert PromotionType.BUY_X_GET_Y == "BUY_X_GET_Y"


@pytest.mark.unit
def test_promotion_status_values():
    assert PromotionStatus.ACTIVE == "ACTIVE"
    assert PromotionStatus.INACTIVE == "INACTIVE"
    assert PromotionStatus.EXPIRED == "EXPIRED"


# --- Domain: Promotion entity ---


@pytest.mark.unit
def test_promotion_create():
    promo = _make_promotion()
    assert promo.code == "SAVE20"
    assert promo.promotion_type == PromotionType.PERCENTAGE
    assert promo.value == Decimal("20")
    assert promo.status == PromotionStatus.ACTIVE
    assert promo.total_uses == 0
    assert len(promo.collect_events()) == 1


@pytest.mark.unit
def test_promotion_create_invalid_code():
    with pytest.raises(ValidationException, match="code"):
        Promotion.create(
            code="",
            description="",
            promotion_type=PromotionType.PERCENTAGE,
            value=Decimal("10"),
            valid_from=NOW,
            valid_until=FUTURE,
        )


@pytest.mark.unit
def test_promotion_create_invalid_value():
    with pytest.raises(ValidationException, match="positive"):
        _make_promotion(value=Decimal("-5"))


@pytest.mark.unit
def test_promotion_create_invalid_dates():
    with pytest.raises(ValidationException, match="after valid_from"):
        _make_promotion(valid_from=FUTURE, valid_until=NOW)


@pytest.mark.unit
def test_promotion_percentage_over_100():
    with pytest.raises(ValidationException, match="100%"):
        _make_promotion(value=Decimal("150"))


@pytest.mark.unit
def test_promotion_is_valid():
    promo = _make_promotion()
    assert promo.is_valid is True


@pytest.mark.unit
def test_promotion_is_not_valid_when_expired():
    promo = _make_promotion(valid_from=PAST - timedelta(days=60), valid_until=PAST)
    assert promo.is_valid is False


@pytest.mark.unit
def test_promotion_is_not_valid_when_inactive():
    promo = _make_promotion()
    promo.deactivate()
    assert promo.is_valid is False


@pytest.mark.unit
def test_promotion_is_not_valid_when_max_uses_reached():
    promo = _make_promotion(max_total_uses=1)
    promo.total_uses = 1
    assert promo.is_valid is False


@pytest.mark.unit
def test_promotion_validate_for_order():
    promo = _make_promotion(min_order_amount=Money(amount=Decimal("50"), currency="USD"))
    order = Money(amount=Decimal("100"), currency="USD")
    promo.validate_for_order(order, customer_usage_count=0)


@pytest.mark.unit
def test_promotion_validate_min_order_fail():
    promo = _make_promotion(min_order_amount=Money(amount=Decimal("50"), currency="USD"))
    order = Money(amount=Decimal("30"), currency="USD")
    with pytest.raises(ValidationException, match="Minimum order"):
        promo.validate_for_order(order, customer_usage_count=0)


@pytest.mark.unit
def test_promotion_validate_max_customer_usage():
    promo = _make_promotion(max_uses_per_customer=1)
    order = Money(amount=Decimal("100"), currency="USD")
    with pytest.raises(ValidationException, match="maximum number"):
        promo.validate_for_order(order, customer_usage_count=1)


@pytest.mark.unit
def test_promotion_calculate_discount_percentage():
    promo = _make_promotion(value=Decimal("20"))
    order = Money(amount=Decimal("100"), currency="USD")
    discount = promo.calculate_discount(order)
    assert discount.amount == Decimal("20.00")
    assert discount.currency == "USD"


@pytest.mark.unit
def test_promotion_calculate_discount_with_max():
    promo = _make_promotion(
        value=Decimal("50"),
        max_discount=Money(amount=Decimal("10"), currency="USD"),
    )
    order = Money(amount=Decimal("100"), currency="USD")
    discount = promo.calculate_discount(order)
    assert discount.amount == Decimal("10")


@pytest.mark.unit
def test_promotion_calculate_discount_fixed_amount():
    promo = _make_promotion(promotion_type=PromotionType.FIXED_AMOUNT, value=Decimal("15"))
    order = Money(amount=Decimal("100"), currency="USD")
    discount = promo.calculate_discount(order)
    assert discount.amount == Decimal("15")


@pytest.mark.unit
def test_promotion_calculate_discount_fixed_exceeds_order():
    promo = _make_promotion(promotion_type=PromotionType.FIXED_AMOUNT, value=Decimal("150"))
    order = Money(amount=Decimal("100"), currency="USD")
    discount = promo.calculate_discount(order)
    assert discount.amount == Decimal("100")


@pytest.mark.unit
def test_promotion_calculate_discount_free_delivery():
    promo = _make_promotion(promotion_type=PromotionType.FREE_DELIVERY, value=Decimal("1"))
    order = Money(amount=Decimal("100"), currency="USD")
    discount = promo.calculate_discount(order)
    assert discount.amount == Decimal("0")


@pytest.mark.unit
def test_promotion_apply():
    promo = _make_promotion()
    promo.collect_events()

    promo.apply(uuid.uuid4(), uuid.uuid4(), Decimal("20"))
    assert promo.total_uses == 1
    events = promo.collect_events()
    assert len(events) == 1
    assert events[0].__class__.__name__ == "CouponApplied"


@pytest.mark.unit
def test_promotion_deactivate():
    promo = _make_promotion()
    promo.collect_events()

    promo.deactivate()
    assert promo.status == PromotionStatus.INACTIVE
    events = promo.collect_events()
    assert len(events) == 1
    assert events[0].__class__.__name__ == "PromotionDeactivated"


# --- Domain: CouponUsage ---


@pytest.mark.unit
def test_coupon_usage_record():
    usage = CouponUsage.record(
        promotion_id=uuid.uuid4(),
        order_id=uuid.uuid4(),
        customer_id=uuid.uuid4(),
        discount_amount=Decimal("15.50"),
        discount_currency="USD",
    )
    assert usage.discount_amount == Decimal("15.50")
    assert usage.discount_currency == "USD"
    assert usage.id is not None


# --- Application: CreatePromotionHandler ---


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_promotion_handler_success():
    promo_repo = AsyncMock()
    promo_repo.get_by_code.return_value = None

    uow = AsyncMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=False)

    handler = CreatePromotionHandler(promo_repo, uow)
    command = CreatePromotionCommand(
        code="SUMMER10",
        description="Summer sale",
        promotion_type=PromotionType.PERCENTAGE,
        value=Decimal("10"),
        valid_from=NOW,
        valid_until=FUTURE,
    )

    promo_id = await handler.handle(command)
    assert promo_id is not None
    promo_repo.add.assert_called_once()
    uow.commit.assert_called_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_promotion_handler_duplicate_code():
    promo_repo = AsyncMock()
    promo_repo.get_by_code.return_value = _make_promotion()

    uow = AsyncMock()
    handler = CreatePromotionHandler(promo_repo, uow)
    command = CreatePromotionCommand(
        code="SAVE20",
        description="dupe",
        promotion_type=PromotionType.PERCENTAGE,
        value=Decimal("20"),
        valid_from=NOW,
        valid_until=FUTURE,
    )

    with pytest.raises(ValidationException, match="already exists"):
        await handler.handle(command)


# --- Application: ApplyPromotionHandler ---


@pytest.mark.unit
@pytest.mark.asyncio
async def test_apply_promotion_handler_success():
    promo = _make_promotion()
    promo.collect_events()

    promo_repo = AsyncMock()
    promo_repo.get_by_code.return_value = promo
    promo_repo.count_customer_usage.return_value = 0

    uow = AsyncMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=False)

    handler = ApplyPromotionHandler(promo_repo, uow)
    command = ApplyPromotionCommand(
        code="SAVE20",
        order_id=uuid.uuid4(),
        customer_id=uuid.uuid4(),
        order_amount=Decimal("100"),
    )

    result = await handler.handle(command)
    assert result.discount_amount == Decimal("20.00")
    assert result.discount_currency == "USD"
    promo_repo.update.assert_called_once()
    promo_repo.add_usage.assert_called_once()
    uow.commit.assert_called_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_apply_promotion_handler_not_found():
    promo_repo = AsyncMock()
    promo_repo.get_by_code.return_value = None

    uow = AsyncMock()
    handler = ApplyPromotionHandler(promo_repo, uow)
    command = ApplyPromotionCommand(
        code="INVALID",
        order_id=uuid.uuid4(),
        customer_id=uuid.uuid4(),
        order_amount=Decimal("100"),
    )

    with pytest.raises(NotFoundException):
        await handler.handle(command)


# --- Application: DeactivatePromotionHandler ---


@pytest.mark.unit
@pytest.mark.asyncio
async def test_deactivate_promotion_handler_success():
    promo = _make_promotion()
    promo.collect_events()

    promo_repo = AsyncMock()
    promo_repo.get_by_id.return_value = promo

    uow = AsyncMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=False)

    handler = DeactivatePromotionHandler(promo_repo, uow)
    command = DeactivatePromotionCommand(promotion_id=promo.id)

    await handler.handle(command)
    assert promo.status == PromotionStatus.INACTIVE
    promo_repo.update.assert_called_once()
    uow.commit.assert_called_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_deactivate_promotion_handler_not_found():
    promo_repo = AsyncMock()
    promo_repo.get_by_id.return_value = None

    uow = AsyncMock()
    handler = DeactivatePromotionHandler(promo_repo, uow)
    command = DeactivatePromotionCommand(promotion_id=uuid.uuid4())

    with pytest.raises(NotFoundException):
        await handler.handle(command)
