import uuid
from dataclasses import dataclass

from modules.notifications.application.ports.notification_dispatcher import NotificationDispatcher
from modules.notifications.application.ports.notification_repository import NotificationRepository
from modules.notifications.domain.entities.notification import Notification, NotificationChannel
from shared.application.ports.unit_of_work import AbstractUnitOfWork


@dataclass(frozen=True)
class SendNotificationCommand:
    recipient_id: uuid.UUID
    channel: NotificationChannel
    title: str
    body: str


class SendNotificationHandler:
    def __init__(
        self,
        notification_repo: NotificationRepository,
        dispatcher: NotificationDispatcher,
        uow: AbstractUnitOfWork,
    ) -> None:
        self._notification_repo = notification_repo
        self._dispatcher = dispatcher
        self._uow = uow

    async def _save(self, notification: Notification) -> None:
        async with self._uow:
            await self._notification_repo.update(notification)
            self._uow.register_aggregate(notification)
            await self._uow.commit()

    async def handle(self, command: SendNotificationCommand) -> uuid.UUID:
        notification = Notification.create(
            recipient_id=command.recipient_id,
            channel=command.channel,
            title=command.title,
            body=command.body,
        )

        async with self._uow:
            await self._notification_repo.add(notification)
            self._uow.register_aggregate(notification)
            await self._uow.commit()

        try:
            await self._dispatcher.dispatch(notification)
            notification.mark_sent()
        except Exception as e:
            notification.mark_failed(str(e))

        await self._save(notification)

        return notification.id
