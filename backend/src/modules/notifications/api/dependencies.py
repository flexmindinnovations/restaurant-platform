from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db_session
from modules.notifications.application.commands.send_notification import SendNotificationHandler
from modules.notifications.application.ports.notification_dispatcher import NotificationDispatcher
from modules.notifications.application.ports.notification_repository import NotificationRepository
from modules.notifications.infrastructure.adapters.composite_notification_dispatcher import (
    CompositeNotificationDispatcher,
)
from modules.notifications.infrastructure.adapters.push_notification_dispatcher import PushNotificationDispatcher
from modules.notifications.infrastructure.adapters.sms_notification_dispatcher import SmsNotificationDispatcher
from modules.notifications.infrastructure.adapters.smtp_notification_dispatcher import SmtpNotificationDispatcher
from modules.notifications.infrastructure.repositories.sqlalchemy_notification_repository import (
    SqlAlchemyNotificationRepository,
)
from shared.application.ports.unit_of_work import AbstractUnitOfWork
from shared.infrastructure.event_bus import get_event_bus
from shared.infrastructure.unit_of_work import SqlAlchemyUnitOfWork


def _notification_repo(session: AsyncSession = Depends(get_db_session)) -> NotificationRepository:
    return SqlAlchemyNotificationRepository(session)


def _notification_dispatcher() -> NotificationDispatcher:
    return CompositeNotificationDispatcher(
        email=SmtpNotificationDispatcher(),
        sms=SmsNotificationDispatcher(),
        push=PushNotificationDispatcher(),
    )


def _uow(session: AsyncSession = Depends(get_db_session)) -> AbstractUnitOfWork:
    return SqlAlchemyUnitOfWork(session, get_event_bus())


def get_send_notification_handler(
    repo: NotificationRepository = Depends(_notification_repo),
    dispatcher: NotificationDispatcher = Depends(_notification_dispatcher),
    uow: AbstractUnitOfWork = Depends(_uow),
) -> SendNotificationHandler:
    return SendNotificationHandler(repo, dispatcher, uow)
