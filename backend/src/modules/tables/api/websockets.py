import json
import uuid

import structlog
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from shared.api.security import decode_token
from shared.infrastructure.redis import get_redis

router = APIRouter()
logger = structlog.get_logger()


@router.websocket("/ws/tables/{restaurant_id}")
async def websocket_table_status(
    websocket: WebSocket,
    restaurant_id: uuid.UUID,
    token: str = Query(...),
) -> None:
    from app.config import get_settings

    settings = get_settings()

    try:
        payload = decode_token(token, settings.jwt_secret_key, settings.jwt_algorithm)
        if payload.get("type") != "access":
            await websocket.close(code=4001, reason="Invalid token type")
            return
    except Exception as e:
        logger.warning("WebSocket table status auth failed", error=str(e))
        await websocket.close(code=4003, reason="Authentication failed")
        return

    await websocket.accept()
    logger.info("WebSocket table status connected", restaurant_id=str(restaurant_id), user_id=payload.get("sub"))

    redis_client = get_redis()
    pubsub = redis_client.pubsub()
    channel = f"tables:{restaurant_id}:status"
    await pubsub.subscribe(channel)

    try:
        async for message in pubsub.listen():
            if message["type"] != "message":
                continue
            try:
                data = json.loads(message["data"])
                await websocket.send_json(data)
            except Exception:
                logger.exception("Failed to forward table status message")
    except WebSocketDisconnect:
        logger.info("WebSocket table status client disconnected", restaurant_id=str(restaurant_id))
    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.close()
