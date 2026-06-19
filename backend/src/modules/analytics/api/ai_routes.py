import pathlib
import sys

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from redis.asyncio import Redis

from app.dependencies import get_redis
from shared.api.response import ResponseEnvelope

# Ensure the AI module can be loaded
ai_path = str((pathlib.Path(__file__).parent / "../../../../../ai/src").resolve())
if ai_path not in sys.path:
    sys.path.append(ai_path)

from gateway.client import GeminiClient  # noqa: E402

ai_router = APIRouter()
MAX_SUPPORT_REQUESTS_PER_MINUTE = 10


class ChatMessage(BaseModel):
    role: str  # "user" or "model"
    text: str


class SupportChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = Field(default_factory=list)


class SupportChatResponse(BaseModel):
    response: str


@ai_router.post("/support/chat", response_model=ResponseEnvelope[SupportChatResponse])
async def support_chat(
    request: Request, payload: SupportChatRequest, redis: Redis = Depends(get_redis)
) -> ResponseEnvelope[SupportChatResponse]:
    client_host = request.client.host if request.client else "unknown"
    rate_limit_key = f"rate_limit:ai_support:{client_host}"

    current_requests = await redis.get(rate_limit_key)
    if current_requests and int(current_requests) >= MAX_SUPPORT_REQUESTS_PER_MINUTE:
        raise HTTPException(
            status_code=429, detail="Rate limit exceeded. Please wait a minute before sending another message."
        )

    await redis.incr(rate_limit_key)
    if not current_requests:
        await redis.expire(rate_limit_key, 60)

    client = GeminiClient()
    system_instruction = (
        "You are an AI customer support assistant for a multi-vendor restaurant ordering platform. "
        "Be helpful, polite, and professional. Provide information about orders, refunds, and menu items."
    )

    formatted_history = [{"role": msg.role, "text": msg.text} for msg in payload.history]
    formatted_history.append({"role": "user", "text": payload.message})

    try:
        assistant_response = await client.generate_content(
            contents=formatted_history, system_instruction=system_instruction
        )
    except Exception:
        assistant_response = (
            f"I'm sorry, I am having trouble connecting to my brain. But you said: '{payload.message}'."
        )

    return ResponseEnvelope(data=SupportChatResponse(response=assistant_response))
