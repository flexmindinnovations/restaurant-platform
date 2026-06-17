import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt

from modules.identity.application.ports.token_service import TokenService


class JwtTokenService(TokenService):
    def __init__(
        self,
        secret_key: str,
        algorithm: str,
        access_expire_minutes: int,
        refresh_expire_days: int,
    ) -> None:
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._access_expire_minutes = access_expire_minutes
        self._refresh_expire_days = refresh_expire_days

    def generate_access_token(self, account_id: uuid.UUID, roles: list[str]) -> str:
        now = datetime.now(UTC)
        payload = {
            "sub": str(account_id),
            "roles": roles,
            "type": "access",
            "exp": now + timedelta(minutes=self._access_expire_minutes),
            "iat": now,
        }
        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def generate_refresh_token(self, account_id: uuid.UUID) -> str:
        now = datetime.now(UTC)
        payload = {
            "sub": str(account_id),
            "type": "refresh",
            "exp": now + timedelta(days=self._refresh_expire_days),
            "iat": now,
        }
        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def decode_access_token(self, token: str) -> dict[str, Any]:
        payload = jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
        if payload.get("type") != "access":
            raise jwt.PyJWTError("Invalid token type")
        return payload

    def decode_refresh_token(self, token: str) -> dict[str, Any]:
        payload = jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
        if payload.get("type") != "refresh":
            raise jwt.PyJWTError("Invalid token type")
        return payload
