import asyncio
import uuid
from celery import shared_task
import structlog
from modules.notifications.infrastructure.repositories.sqlalchemy_notification_repository import (
    SqlAlchemyNotificationRepository,
)
from modules.notifications.infrastructure.adapters.composite_notification_dispatcher import (
    CompositeNotificationDispatcher,
)
from modules.notifications.infrastructure.adapters.push_notification_dispatcher import PushNotificationDispatcher
from modules.notifications.infrastructure.adapters.sms_notification_dispatcher import SmsNotificationDispatcher
from modules.notifications.infrastructure.adapters.smtp_notification_dispatcher import SmtpNotificationDispatcher
from shared.infrastructure.database import get_session_factory

logger = structlog.get_logger()

async def send_notification_async(notification_id: str) -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        repo = SqlAlchemyNotificationRepository(session)
        notification = await repo.get_by_id(uuid.UUID(notification_id))
        if not notification:
            logger.error("Notification not found for async dispatch", notification_id=notification_id)
            return

        dispatcher = CompositeNotificationDispatcher(
            email=SmtpNotificationDispatcher(),
            sms=SmsNotificationDispatcher(),
            push=PushNotificationDispatcher(),
        )
        
        try:
            await dispatcher.dispatch(notification)
            notification.mark_sent()
        except Exception as e:
            logger.error("Failed to dispatch notification in background", notification_id=notification_id, error=str(e))
            notification.mark_failed(str(e))
        
        await repo.update(notification)
        await session.commit()


@shared_task(name="workers.tasks.send_notification_task")
def send_notification_task(notification_id: str) -> None:
    asyncio.run(send_notification_async(notification_id))
