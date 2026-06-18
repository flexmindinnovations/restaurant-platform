from abc import ABC, abstractmethod

from modules.notifications.domain.entities.notification import Notification


class NotificationDispatcher(ABC):
    @abstractmethod
    async def dispatch(self, notification: Notification) -> None:
        pass
