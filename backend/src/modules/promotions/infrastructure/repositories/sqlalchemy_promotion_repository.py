import uuid
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.promotions.application.ports.promotion_repository import PromotionRepository
from modules.promotions.domain.entities.coupon_usage import CouponUsage
from modules.promotions.domain.entities.promotion import Promotion
from modules.promotions.domain.value_objects.promotion_status import PromotionStatus
from modules.promotions.domain.value_objects.promotion_type import PromotionType
from modules.promotions.infrastructure.models.promotion_models import CouponUsageModel, PromotionModel
from shared.domain.value_objects import Money


class SqlAlchemyPromotionRepository(PromotionRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, promotion: Promotion) -> None:
        model = PromotionModel(
            id=promotion.id,
            code=promotion.code,
            description=promotion.description,
            promotion_type=promotion.promotion_type.value,
            value=promotion.value,
            min_order_amount=promotion.min_order_amount.amount if promotion.min_order_amount else None,
            min_order_currency=promotion.min_order_amount.currency if promotion.min_order_amount else None,
            max_discount_amount=promotion.max_discount.amount if promotion.max_discount else None,
            max_discount_currency=promotion.max_discount.currency if promotion.max_discount else None,
            valid_from=promotion.valid_from,
            valid_until=promotion.valid_until,
            max_total_uses=promotion.max_total_uses,
            max_uses_per_customer=promotion.max_uses_per_customer,
            total_uses=promotion.total_uses,
            status=promotion.status.value,
            restaurant_id=promotion.restaurant_id,
            created_at=promotion.created_at,
            updated_at=promotion.updated_at,
        )
        self._session.add(model)

    async def get_by_id(self, promotion_id: uuid.UUID) -> Promotion | None:
        result = await self._session.execute(select(PromotionModel).where(PromotionModel.id == promotion_id))
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def get_by_code(self, code: str) -> Promotion | None:
        result = await self._session.execute(select(PromotionModel).where(PromotionModel.code == code))
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def update(self, promotion: Promotion) -> None:
        result = await self._session.execute(select(PromotionModel).where(PromotionModel.id == promotion.id))
        model = result.scalar_one_or_none()
        if model:
            model.description = promotion.description
            model.value = promotion.value
            model.total_uses = promotion.total_uses
            model.status = promotion.status.value
            model.updated_at = promotion.updated_at

    async def list_all(self, skip: int = 0, limit: int = 10) -> tuple[list[Promotion], int]:
        base_query = select(PromotionModel)
        count_query = select(func.count()).select_from(base_query.subquery())
        total = await self._session.scalar(count_query) or 0

        result = await self._session.execute(
            base_query.order_by(PromotionModel.created_at.desc()).offset(skip).limit(limit)
        )
        models = result.scalars().all()
        return [self._to_domain(m) for m in models], total

    async def list_available(self, skip: int = 0, limit: int = 10) -> tuple[list[Promotion], int]:
        now = datetime.now(UTC)
        base_query = (
            select(PromotionModel)
            .where(PromotionModel.status == PromotionStatus.ACTIVE.value)
            .where(PromotionModel.valid_from <= now)
            .where(PromotionModel.valid_until > now)
        )
        count_query = select(func.count()).select_from(base_query.subquery())
        total = await self._session.scalar(count_query) or 0

        result = await self._session.execute(
            base_query.order_by(PromotionModel.valid_until.asc()).offset(skip).limit(limit)
        )
        models = result.scalars().all()
        return [self._to_domain(m) for m in models], total

    async def add_usage(self, usage: CouponUsage) -> None:
        model = CouponUsageModel(
            id=usage.id,
            promotion_id=usage.promotion_id,
            order_id=usage.order_id,
            customer_id=usage.customer_id,
            discount_amount=usage.discount_amount,
            discount_currency=usage.discount_currency,
            created_at=usage.created_at,
            updated_at=usage.updated_at,
        )
        self._session.add(model)

    async def count_customer_usage(self, promotion_id: uuid.UUID, customer_id: uuid.UUID) -> int:
        result = await self._session.scalar(
            select(func.count())
            .select_from(CouponUsageModel)
            .where(CouponUsageModel.promotion_id == promotion_id)
            .where(CouponUsageModel.customer_id == customer_id)
        )
        return result or 0

    def _to_domain(self, model: PromotionModel) -> Promotion:
        min_order = (
            Money(amount=Decimal(str(model.min_order_amount)), currency=model.min_order_currency)
            if model.min_order_amount is not None and model.min_order_currency
            else None
        )
        max_disc = (
            Money(amount=Decimal(str(model.max_discount_amount)), currency=model.max_discount_currency)
            if model.max_discount_amount is not None and model.max_discount_currency
            else None
        )

        return Promotion(
            id=model.id,
            code=model.code,
            description=model.description,
            promotion_type=PromotionType(model.promotion_type),
            value=Decimal(str(model.value)),
            min_order_amount=min_order,
            max_discount=max_disc,
            valid_from=model.valid_from,
            valid_until=model.valid_until,
            max_total_uses=model.max_total_uses,
            max_uses_per_customer=model.max_uses_per_customer,
            total_uses=model.total_uses,
            status=PromotionStatus(model.status),
            restaurant_id=model.restaurant_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
