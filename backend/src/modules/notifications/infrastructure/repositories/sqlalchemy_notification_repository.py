import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.notifications.application.ports.notification_repository import NotificationRepository
from modules.notifications.domain.entities.notification import Notification, NotificationChannel, NotificationStatus
from modules.notifications.infrastructure.models.notifications_models import NotificationModel


class SqlAlchemyNotificationRepository(NotificationRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_entity(self, model: NotificationModel) -> Notification:
        entity = Notification(
            id=model.id,
            recipient_id=model.recipient_id,
            channel=NotificationChannel(model.channel),
            title=model.title,
            body=model.body,
            status=NotificationStatus(model.status),
            sent_at=model.sent_at,
            error_message=model.error_message,
        )
        entity.created_at = model.created_at
        entity.updated_at = model.updated_at
        return entity

    async def add(self, notification: Notification) -> None:
        model = NotificationModel(
            id=notification.id,
            recipient_id=notification.recipient_id,
            channel=notification.channel.value if hasattr(notification.channel, "value") else str(notification.channel),
            title=notification.title,
            body=notification.body,
            status=notification.status.value if hasattr(notification.status, "value") else str(notification.status),
            sent_at=notification.sent_at,
            error_message=notification.error_message,
            created_at=notification.created_at,
            updated_at=notification.updated_at,
        )
        self._session.add(model)

    async def update(self, notification: Notification) -> None:
        result = await self._session.execute(select(NotificationModel).where(NotificationModel.id == notification.id))
        model = result.scalar_one_or_none()
        if model:
            status = notification.status
            model.status = status.value if hasattr(status, "value") else str(status)
            model.sent_at = notification.sent_at
            model.error_message = notification.error_message
            model.updated_at = notification.updated_at

    async def get_by_id(self, notification_id: uuid.UUID) -> Notification | None:
        result = await self._session.execute(select(NotificationModel).where(NotificationModel.id == notification_id))
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None
