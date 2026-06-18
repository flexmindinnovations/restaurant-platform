import uuid
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.orders.application.ports.order_repository import OrderRepository
from modules.orders.domain.entities.order import Order
from modules.orders.domain.entities.order_item import OrderItem
from modules.orders.domain.value_objects.order_number import OrderNumber
from modules.orders.domain.value_objects.order_status import OrderStatus
from modules.orders.infrastructure.models.order_models import OrderItemModel, OrderModel
from shared.domain.value_objects import Money


class SqlAlchemyOrderRepository(OrderRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, order: Order) -> None:
        model = OrderModel(
            id=order.id,
            restaurant_id=order.restaurant_id,
            customer_id=order.customer_id,
            order_number=order.order_number.value,
            status=order.status.value,
            delivery_address_street=order.delivery_address_street,
            delivery_address_city=order.delivery_address_city,
            delivery_address_state=order.delivery_address_state,
            delivery_address_postal_code=order.delivery_address_postal_code,
            delivery_address_country=order.delivery_address_country,
            delivery_notes=order.delivery_notes,
            subtotal_amount=order.subtotal.amount,
            subtotal_currency=order.subtotal.currency,
            tax_amount=order.tax.amount,
            tax_currency=order.tax.currency,
            delivery_fee_amount=order.delivery_fee.amount,
            delivery_fee_currency=order.delivery_fee.currency,
            tip_amount=order.tip.amount,
            tip_currency=order.tip.currency,
            total_amount=order.total_amount.amount,
            total_currency=order.total_amount.currency,
            cancellation_reason=order.cancellation_reason,
            placed_at=order.placed_at,
            confirmed_at=order.confirmed_at,
            preparing_at=order.preparing_at,
            ready_at=order.ready_at,
            picked_up_at=order.picked_up_at,
            delivered_at=order.delivered_at,
            cancelled_at=order.cancelled_at,
            created_at=order.created_at,
            updated_at=order.updated_at,
        )

        item_models = [
            OrderItemModel(
                id=item.id,
                order_id=order.id,
                menu_item_id=item.menu_item_id,
                name=item.name,
                price_amount=item.unit_price.amount,
                price_currency=item.unit_price.currency,
                quantity=item.quantity,
                special_instructions=item.special_instructions,
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
            for item in order.items
        ]
        model.items = item_models
        self._session.add(model)

    async def get_by_id(self, order_id: uuid.UUID) -> Order | None:
        result = await self._session.execute(select(OrderModel).where(OrderModel.id == order_id))
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_domain(model)

    async def get_by_order_number(self, order_number: str) -> Order | None:
        result = await self._session.execute(select(OrderModel).where(OrderModel.order_number == order_number))
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_domain(model)

    async def update(self, order: Order) -> None:
        result = await self._session.execute(select(OrderModel).where(OrderModel.id == order.id))
        model = result.scalar_one_or_none()
        if model:
            model.status = order.status.value
            model.cancellation_reason = order.cancellation_reason
            model.confirmed_at = order.confirmed_at
            model.preparing_at = order.preparing_at
            model.ready_at = order.ready_at
            model.picked_up_at = order.picked_up_at
            model.delivered_at = order.delivered_at
            model.cancelled_at = order.cancelled_at
            model.updated_at = order.updated_at

    async def list_by_customer(
        self, customer_id: uuid.UUID, skip: int = 0, limit: int = 10
    ) -> tuple[list[Order], int]:
        base_query = select(OrderModel).where(OrderModel.customer_id == customer_id)
        count_query = select(func.count()).select_from(base_query.subquery())
        total = await self._session.scalar(count_query) or 0

        result = await self._session.execute(
            base_query.order_by(OrderModel.placed_at.desc()).offset(skip).limit(limit)
        )
        models = result.scalars().all()
        return [self._to_domain(m) for m in models], total

    async def list_by_restaurant(
        self,
        restaurant_id: uuid.UUID,
        status: OrderStatus | None = None,
        skip: int = 0,
        limit: int = 10,
    ) -> tuple[list[Order], int]:
        base_query = select(OrderModel).where(OrderModel.restaurant_id == restaurant_id)
        if status:
            base_query = base_query.where(OrderModel.status == status.value)

        count_query = select(func.count()).select_from(base_query.subquery())
        total = await self._session.scalar(count_query) or 0

        result = await self._session.execute(
            base_query.order_by(OrderModel.placed_at.desc()).offset(skip).limit(limit)
        )
        models = result.scalars().all()
        return [self._to_domain(m) for m in models], total

    def _to_domain(self, model: OrderModel) -> Order:
        items = [
            OrderItem(
                id=item.id,
                order_id=item.order_id,
                menu_item_id=item.menu_item_id,
                name=item.name,
                unit_price=Money(amount=Decimal(str(item.price_amount)), currency=item.price_currency),
                quantity=item.quantity,
                special_instructions=item.special_instructions,
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
            for item in model.items
        ]
        return Order(
            id=model.id,
            restaurant_id=model.restaurant_id,
            customer_id=model.customer_id,
            order_number=OrderNumber(model.order_number),
            status=OrderStatus(model.status),
            items=items,
            delivery_address_street=model.delivery_address_street,
            delivery_address_city=model.delivery_address_city,
            delivery_address_state=model.delivery_address_state,
            delivery_address_postal_code=model.delivery_address_postal_code,
            delivery_address_country=model.delivery_address_country,
            delivery_notes=model.delivery_notes,
            subtotal=Money(amount=Decimal(str(model.subtotal_amount)), currency=model.subtotal_currency),
            tax=Money(amount=Decimal(str(model.tax_amount)), currency=model.tax_currency),
            delivery_fee=Money(amount=Decimal(str(model.delivery_fee_amount)), currency=model.delivery_fee_currency),
            tip=Money(amount=Decimal(str(model.tip_amount)), currency=model.tip_currency),
            total_amount=Money(amount=Decimal(str(model.total_amount)), currency=model.total_currency),
            cancellation_reason=model.cancellation_reason,
            placed_at=model.placed_at,
            confirmed_at=model.confirmed_at,
            preparing_at=model.preparing_at,
            ready_at=model.ready_at,
            picked_up_at=model.picked_up_at,
            delivered_at=model.delivered_at,
            cancelled_at=model.cancelled_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
