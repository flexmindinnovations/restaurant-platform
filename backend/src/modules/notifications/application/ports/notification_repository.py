import uuid
from abc import ABC, abstractmethod

from modules.notifications.domain.entities.notification import Notification


class NotificationRepository(ABC):
    @abstractmethod
    async def add(self, notification: Notification) -> None:
        pass

    @abstractmethod
    async def update(self, notification: Notification) -> None:
        pass

    @abstractmethod
    async def get_by_id(self, notification_id: uuid.UUID) -> Notification | None:
        pass
