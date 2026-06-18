import uuid
from typing import Any

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field

from modules.notifications.api.dependencies import get_send_notification_handler
from modules.notifications.application.commands.send_notification import (
    SendNotificationCommand,
    SendNotificationHandler,
)
from modules.notifications.domain.entities.notification import NotificationChannel
from shared.api.response import ResponseEnvelope
from shared.api.security import require_roles

router = APIRouter()


class SendNotificationRequest(BaseModel):
    recipient_id: uuid.UUID
    channel: str = Field("EMAIL", description="EMAIL, SMS, PUSH")
    title: str = Field(..., max_length=255)
    body: str = Field(..., max_length=1000)


@router.post("/send", response_model=ResponseEnvelope[uuid.UUID], status_code=status.HTTP_201_CREATED)
async def send_notification(
    request: SendNotificationRequest,
    _current_user: dict[str, Any] = Depends(require_roles("SUPER_ADMIN")),
    handler: SendNotificationHandler = Depends(get_send_notification_handler),
) -> ResponseEnvelope[uuid.UUID]:
    command = SendNotificationCommand(
        recipient_id=request.recipient_id,
        channel=NotificationChannel(request.channel),
        title=request.title,
        body=request.body,
    )
    notification_id = await handler.handle(command)
    return ResponseEnvelope(data=notification_id)
