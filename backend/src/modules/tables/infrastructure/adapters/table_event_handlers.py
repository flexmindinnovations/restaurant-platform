import json

import structlog

from modules.tables.domain.events.table_events import TableStatusChanged
from shared.infrastructure.redis import get_redis

logger = structlog.get_logger()


async def broadcast_table_status_changed(event: TableStatusChanged) -> None:
    """Publish table status change to Redis pub/sub for WebSocket broadcasting."""
    redis_client = get_redis()
    channel = f"tables:{event.restaurant_id}:status"
    payload = json.dumps({
        "type": "table_status_changed",
        "table_id": str(event.table_id),
        "restaurant_id": str(event.restaurant_id),
        "old_status": str(event.old_status),
        "new_status": str(event.new_status),
        "changed_by": str(event.changed_by) if event.changed_by else None,
        "occurred_at": event.occurred_at.isoformat() if hasattr(event, "occurred_at") else None,
    })
    await redis_client.publish(channel, payload)
    logger.info(
        "table_status_broadcast",
        table_id=str(event.table_id),
        old_status=str(event.old_status),
        new_status=str(event.new_status),
    )


def register_table_event_handlers(event_bus: "InMemoryEventBus") -> None:  # noqa: F821
    """Register all table module event handlers with the event bus."""
    from shared.infrastructure.event_bus import InMemoryEventBus

    assert isinstance(event_bus, InMemoryEventBus)
    event_bus.subscribe(TableStatusChanged, broadcast_table_status_changed)
    logger.info("table_event_handlers_registered")
