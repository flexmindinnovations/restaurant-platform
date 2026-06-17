import uuid
from collections.abc import Awaitable, Callable
from typing import Annotated, Any

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.dependencies import get_db_session

security_scheme = HTTPBearer()

OwnershipChecker = Callable[[uuid.UUID, AsyncSession], Awaitable[uuid.UUID | None]]

_ownership_checker: OwnershipChecker | None = None


def register_ownership_checker(checker: OwnershipChecker) -> None:
    global _ownership_checker  # noqa: PLW0603
    _ownership_checker = checker


def decode_token(token: str, secret_key: str, algorithm: str) -> dict[str, Any]:
    return jwt.decode(token, secret_key, algorithms=[algorithm])


def create_token(payload: dict[str, Any], secret_key: str, algorithm: str) -> str:
    return jwt.encode(payload, secret_key, algorithm=algorithm)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security_scheme)],
    settings=Depends(get_settings),
) -> dict[str, Any]:
    token = credentials.credentials
    try:
        payload = decode_token(token, settings.jwt_secret_key, settings.jwt_algorithm)
        if payload.get("type") != "access":
            raise jwt.PyJWTError("Invalid token type")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )


def require_roles(*allowed_roles: str):
    def dependency(current_user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
        user_roles = current_user.get("roles", [])
        if "SUPER_ADMIN" in user_roles:
            return current_user
        if not any(role in user_roles for role in allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this resource",
            )
        return current_user
    return dependency


async def _set_rls_context(session: AsyncSession, restaurant_id: uuid.UUID) -> None:
    await session.execute(
        text("SELECT set_config('app.current_restaurant_id', :val, true)"),
        {"val": str(restaurant_id)},
    )


async def require_restaurant_access(
    restaurant_id: uuid.UUID,
    current_user: dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> uuid.UUID:
    user_id = uuid.UUID(current_user["sub"])
    roles = current_user.get("roles", [])

    if "SUPER_ADMIN" in roles:
        await _set_rls_context(session, restaurant_id)
        return restaurant_id

    if _ownership_checker is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to this restaurant is denied",
        )

    owner_id = await _ownership_checker(restaurant_id, session)
    if owner_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")

    if "RESTAURANT_OWNER" in roles and owner_id == user_id:
        await _set_rls_context(session, restaurant_id)
        return restaurant_id

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access to this restaurant is denied",
    )
