import json
import time
import uuid

import structlog
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.config import get_settings
from shared.api.security import decode_token
from shared.infrastructure.redis import get_redis

router = APIRouter()
logger = structlog.get_logger()


@router.websocket("/ws/orders/{order_id}/tracking")
async def websocket_tracking(
    websocket: WebSocket,
    order_id: uuid.UUID,
    token: str = Query(...),
) -> None:
    settings = get_settings()

    # 1. Authenticate token
    try:
        payload = decode_token(token, settings.jwt_secret_key, settings.jwt_algorithm)
        if payload.get("type") != "access":
            await websocket.close(code=4001, reason="Invalid token type")
            return
    except Exception as e:
        logger.warning("WebSocket handshake authentication failed", error=str(e))
        await websocket.close(code=4003, reason="Authentication failed")
        return

    # 2. Accept connection
    await websocket.accept()
    logger.info("WebSocket tracking connected", order_id=str(order_id), user_id=payload.get("sub"))

    # 3. Subscribe to Redis tracking updates
    redis_client = get_redis()
    pubsub = redis_client.pubsub()
    channel = f"order:{order_id}:tracking"
    await pubsub.subscribe(channel)

    last_sent_time = 0.0
    throttle_interval = 5.0

    try:
        async for message in pubsub.listen():
            if message["type"] != "message":
                continue
            last_sent_time = await _process_message(
                message, websocket, last_sent_time, throttle_interval,
            )
    except WebSocketDisconnect:
        logger.info("WebSocket tracking client disconnected", order_id=str(order_id))
    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.close()


async def _process_message(
    message: dict,
    websocket: WebSocket,
    last_sent_time: float,
    throttle_interval: float,
) -> float:
    try:
        data = json.loads(message["data"])
    except Exception:
        logger.exception("Failed to parse WebSocket message")
        return last_sent_time

    is_location = "latitude" in data and "longitude" in data
    current_time = time.time()

    if not is_location or (current_time - last_sent_time >= throttle_interval):
        await websocket.send_json(data)
        if is_location:
            return current_time
    return last_sent_time
