import asyncio
import smtplib
from email.message import EmailMessage

import structlog

from modules.notifications.application.ports.notification_dispatcher import NotificationDispatcher
from modules.notifications.domain.entities.notification import Notification, NotificationChannel

logger = structlog.get_logger()


class SmtpNotificationDispatcher(NotificationDispatcher):
    def __init__(self, smtp_host: str = "localhost", smtp_port: int = 1025) -> None:
        self._host = smtp_host
        self._port = smtp_port

    async def dispatch(self, notification: Notification) -> None:
        if notification.channel == NotificationChannel.EMAIL:
            await self._send_email(notification)
        else:
            await self._send_log(notification)

    async def _send_email(self, notification: Notification) -> None:
        msg = EmailMessage()
        msg["Subject"] = notification.title
        msg["From"] = "noreply@restaurantplatform.com"
        msg["To"] = f"{notification.recipient_id}@example.com"  # Using recipient_id as placeholder email
        msg.set_content(notification.body)

        try:
            # Execute blocking smtplib operations in a thread pool
            def send():
                with smtplib.SMTP(self._host, self._port, timeout=2.0) as server:
                    server.send_message(msg)

            await asyncio.to_thread(send)
            logger.info(
                "Email notification sent via SMTP",
                notification_id=str(notification.id),
                recipient=str(notification.recipient_id),
            )
        except Exception as e:
            logger.warning(
                "SMTP dispatch failed, falling back to logger",
                error=str(e),
                notification_id=str(notification.id),
                recipient=str(notification.recipient_id),
            )
            await self._send_log(notification)

    async def _send_log(self, notification: Notification) -> None:
        logger.info(
            "Notification Dispatch Log",
            notification_id=str(notification.id),
            recipient_id=str(notification.recipient_id),
            channel=notification.channel,
            title=notification.title,
            body=notification.body,
        )
