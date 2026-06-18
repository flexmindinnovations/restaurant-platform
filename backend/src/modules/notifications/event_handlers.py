from typing import Any

from sqlalchemy import text

from modules.notifications.application.commands.send_notification import (
    SendNotificationCommand,
    SendNotificationHandler,
)
from modules.notifications.domain.entities.notification import NotificationChannel
from modules.notifications.infrastructure.adapters.composite_notification_dispatcher import (
    CompositeNotificationDispatcher,
)
from modules.notifications.infrastructure.adapters.push_notification_dispatcher import PushNotificationDispatcher
from modules.notifications.infrastructure.adapters.sms_notification_dispatcher import SmsNotificationDispatcher
from modules.notifications.infrastructure.adapters.smtp_notification_dispatcher import SmtpNotificationDispatcher
from modules.notifications.infrastructure.repositories.sqlalchemy_notification_repository import (
    SqlAlchemyNotificationRepository,
)
from shared.infrastructure.database import get_session_factory
from shared.infrastructure.event_bus import InMemoryEventBus, get_event_bus
from shared.infrastructure.unit_of_work import SqlAlchemyUnitOfWork

_PARTNER_ASSIGNED_QUERY = text("""
    SELECT
        d.order_id,
        o.customer_id,
        p.name as partner_name
    FROM deliveries.deliveries d
    JOIN orders.orders o ON d.order_id = o.id
    JOIN deliveries.delivery_partners p ON d.partner_id = p.id
    WHERE d.id = :delivery_id
""")

_CUSTOMER_ID_QUERY = text("""
    SELECT customer_id FROM orders.orders WHERE id = :order_id
""")


async def handle_partner_assigned(event: Any) -> None:
    session_factory = get_session_factory()
    delivery_id = event.delivery_id
    partner_id = event.partner_id

    async with session_factory() as session:
        result = await session.execute(_PARTNER_ASSIGNED_QUERY, {"delivery_id": delivery_id})
        row = result.first()
        if not row:
            return

        order_id, customer_id, partner_name = row[0], row[1], row[2]

        repo = SqlAlchemyNotificationRepository(session)
        dispatcher = CompositeNotificationDispatcher(
            email=SmtpNotificationDispatcher(),
            sms=SmsNotificationDispatcher(),
            push=PushNotificationDispatcher(),
        )
        event_bus = get_event_bus()
        uow = SqlAlchemyUnitOfWork(session, event_bus)
        handler = SendNotificationHandler(repo, dispatcher, uow)

        customer_cmd = SendNotificationCommand(
            recipient_id=customer_id,
            channel=NotificationChannel.EMAIL,
            title="Delivery Partner Assigned",
            body=f"Great news! Delivery partner {partner_name} has been assigned to your order {order_id}.",
        )
        await handler.handle(customer_cmd)

        partner_cmd = SendNotificationCommand(
            recipient_id=partner_id,
            channel=NotificationChannel.SMS,
            title="New Assignment",
            body=f"Hello {partner_name}, you have been assigned to delivery {delivery_id}. Check your app.",
        )
        await handler.handle(partner_cmd)


async def handle_order_placed(event: Any) -> None:
    session_factory = get_session_factory()
    order_id = event.aggregate_id
    customer_id = event.customer_id

    async with session_factory() as session:
        repo = SqlAlchemyNotificationRepository(session)
        dispatcher = CompositeNotificationDispatcher(
            email=SmtpNotificationDispatcher(),
            sms=SmsNotificationDispatcher(),
            push=PushNotificationDispatcher(),
        )
        event_bus = get_event_bus()
        uow = SqlAlchemyUnitOfWork(session, event_bus)
        handler = SendNotificationHandler(repo, dispatcher, uow)

        cmd = SendNotificationCommand(
            recipient_id=customer_id,
            channel=NotificationChannel.EMAIL,
            title="Order Placed Successfully",
            body=f"Your order {order_id} has been placed successfully and is pending confirmation.",
        )
        await handler.handle(cmd)


async def handle_order_confirmed(event: Any) -> None:
    session_factory = get_session_factory()
    order_id = event.aggregate_id

    async with session_factory() as session:
        result = await session.execute(_CUSTOMER_ID_QUERY, {"order_id": order_id})
        row = result.first()
        if not row:
            return
        customer_id = row[0]

        repo = SqlAlchemyNotificationRepository(session)
        dispatcher = CompositeNotificationDispatcher(
            email=SmtpNotificationDispatcher(),
            sms=SmsNotificationDispatcher(),
            push=PushNotificationDispatcher(),
        )
        event_bus = get_event_bus()
        uow = SqlAlchemyUnitOfWork(session, event_bus)
        handler = SendNotificationHandler(repo, dispatcher, uow)

        cmd = SendNotificationCommand(
            recipient_id=customer_id,
            channel=NotificationChannel.EMAIL,
            title="Order Confirmed",
            body=f"Great news! Your order {order_id} has been confirmed by the restaurant.",
        )
        await handler.handle(cmd)


async def handle_delivery_completed(event: Any) -> None:
    session_factory = get_session_factory()
    order_id = event.order_id

    async with session_factory() as session:
        result = await session.execute(_CUSTOMER_ID_QUERY, {"order_id": order_id})
        row = result.first()
        if not row:
            return
        customer_id = row[0]

        repo = SqlAlchemyNotificationRepository(session)
        dispatcher = CompositeNotificationDispatcher(
            email=SmtpNotificationDispatcher(),
            sms=SmsNotificationDispatcher(),
            push=PushNotificationDispatcher(),
        )
        event_bus = get_event_bus()
        uow = SqlAlchemyUnitOfWork(session, event_bus)
        handler = SendNotificationHandler(repo, dispatcher, uow)

        cmd = SendNotificationCommand(
            recipient_id=customer_id,
            channel=NotificationChannel.EMAIL,
            title="Order Delivered",
            body=f"Your order {order_id} has been successfully delivered. Enjoy your meal!",
        )
        await handler.handle(cmd)


def register_event_handlers(event_bus: InMemoryEventBus) -> None:
    event_bus.subscribe_by_name("PartnerAssigned", handle_partner_assigned)
    event_bus.subscribe_by_name("OrderPlaced", handle_order_placed)
    event_bus.subscribe_by_name("OrderConfirmed", handle_order_confirmed)
    event_bus.subscribe_by_name("DeliveryCompleted", handle_delivery_completed)
