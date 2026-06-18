from modules.notifications.application.ports.notification_dispatcher import NotificationDispatcher
from modules.notifications.domain.entities.notification import Notification, NotificationChannel


class CompositeNotificationDispatcher(NotificationDispatcher):
    def __init__(
        self,
        email: NotificationDispatcher,
        sms: NotificationDispatcher,
        push: NotificationDispatcher,
    ) -> None:
        self._dispatchers: dict[NotificationChannel, NotificationDispatcher] = {
            NotificationChannel.EMAIL: email,
            NotificationChannel.SMS: sms,
            NotificationChannel.PUSH: push,
        }

    async def dispatch(self, notification: Notification) -> None:
        dispatcher = self._dispatchers[notification.channel]
        await dispatcher.dispatch(notification)
