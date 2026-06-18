from typing import Any

from modules.orders.application.commands.update_order_status import UpdateOrderStatusCommand, UpdateOrderStatusHandler
from modules.orders.domain.value_objects.order_status import OrderStatus
from modules.orders.infrastructure.repositories.sqlalchemy_order_repository import SqlAlchemyOrderRepository
from shared.infrastructure.database import get_session_factory
from shared.infrastructure.event_bus import InMemoryEventBus, get_event_bus
from shared.infrastructure.unit_of_work import SqlAlchemyUnitOfWork


async def handle_delivery_completed(event: Any) -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        order_repo = SqlAlchemyOrderRepository(session)
        event_bus = get_event_bus()
        uow = SqlAlchemyUnitOfWork(session, event_bus)
        handler = UpdateOrderStatusHandler(order_repo, uow)

        command = UpdateOrderStatusCommand(
            order_id=event.order_id,
            status=OrderStatus.COMPLETED,
        )
        await handler.handle(command)


def register_event_handlers(event_bus: InMemoryEventBus) -> None:
    event_bus.subscribe_by_name("DeliveryCompleted", handle_delivery_completed)
