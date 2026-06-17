from collections.abc import AsyncGenerator
from functools import lru_cache
from typing import Any

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from shared.infrastructure.database import get_session
from shared.infrastructure.redis import get_redis as redis_client_factory


@lru_cache
def get_cached_settings() -> Settings:
    return get_settings()


async def get_db_session() -> AsyncGenerator[AsyncSession]:
    """Provide an asynchronous database session context."""
    async for session in get_session():
        yield session


def get_redis() -> Redis:
    """Provide a Redis client connected to the shared Valkey/Redis pool."""
    return redis_client_factory()


def get_current_user(settings: Settings = Depends(get_cached_settings)) -> dict[str, Any]:  # noqa: ARG001
    """Authorization dependency placeholder. Returns a mock user representation."""
    return {
        "id": "00000000-0000-0000-0000-000000000000",
        "email": "placeholder@example.com",
        "roles": ["admin"],
    }
