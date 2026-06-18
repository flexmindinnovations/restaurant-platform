import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum

from shared.domain.entity import AggregateRoot


class NotificationChannel(StrEnum):
    EMAIL = "EMAIL"
    SMS = "SMS"
    PUSH = "PUSH"


class NotificationStatus(StrEnum):
    PENDING = "PENDING"
    SENT = "SENT"
    FAILED = "FAILED"


@dataclass
class Notification(AggregateRoot):
    recipient_id: uuid.UUID = None  # type: ignore[assignment]
    channel: NotificationChannel = NotificationChannel.EMAIL
    title: str = ""
    body: str = ""
    status: NotificationStatus = NotificationStatus.PENDING
    sent_at: datetime | None = None
    error_message: str | None = None

    @classmethod
    def create(
        cls,
        recipient_id: uuid.UUID,
        channel: NotificationChannel,
        title: str,
        body: str,
    ) -> "Notification":
        now = datetime.now(UTC)
        return cls(
            id=uuid.uuid4(),
            recipient_id=recipient_id,
            channel=channel,
            title=title,
            body=body,
            status=NotificationStatus.PENDING,
            created_at=now,
            updated_at=now,
        )

    def mark_sent(self) -> None:
        self.status = NotificationStatus.SENT
        self.sent_at = datetime.now(UTC)
        self.updated_at = datetime.now(UTC)

    def mark_failed(self, error_message: str) -> None:
        self.status = NotificationStatus.FAILED
        self.error_message = error_message
        self.updated_at = datetime.now(UTC)
