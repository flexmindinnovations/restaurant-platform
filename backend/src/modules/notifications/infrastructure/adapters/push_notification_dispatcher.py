import structlog

from modules.notifications.application.ports.notification_dispatcher import NotificationDispatcher
from modules.notifications.domain.entities.notification import Notification

logger = structlog.get_logger()


class PushNotificationDispatcher(NotificationDispatcher):
    async def dispatch(self, notification: Notification) -> None:
        logger.info(
            "Push dispatch (placeholder — no FCM/APNs configured)",
            notification_id=str(notification.id),
            recipient_id=str(notification.recipient_id),
            title=notification.title,
        )
