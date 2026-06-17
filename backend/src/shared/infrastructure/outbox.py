import json
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import DateTime, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from shared.domain.events import DomainEvent
from shared.infrastructure.database import Base


class OutboxMessage(Base):
    __tablename__ = "outbox_messages"
    __table_args__ = {"schema": "shared"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    aggregate_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    event_type: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)


async def store_outbox_events(session: AsyncSession, events: list[DomainEvent]) -> None:
    for event in events:
        payload: dict[str, Any] = {}
        for k, v in event.__dict__.items():
            if isinstance(v, uuid.UUID):
                payload[k] = str(v)
            elif isinstance(v, datetime):
                payload[k] = v.isoformat()
            else:
                payload[k] = v
        msg = OutboxMessage(
            id=event.event_id,
            aggregate_id=event.aggregate_id,
            event_type=type(event).__name__,
            payload=payload,
            occurred_at=event.occurred_at,
        )
        session.add(msg)
