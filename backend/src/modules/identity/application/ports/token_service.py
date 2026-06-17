import uuid
from abc import ABC, abstractmethod
from typing import Any


class TokenService(ABC):
    @abstractmethod
    def generate_access_token(self, account_id: uuid.UUID, roles: list[str]) -> str:
        """Generate a short-lived access token."""

    @abstractmethod
    def generate_refresh_token(self, account_id: uuid.UUID) -> str:
        """Generate a long-lived refresh token."""

    @abstractmethod
    def decode_access_token(self, token: str) -> dict[str, Any]:
        """Decode and validate an access token, returning the payload."""

    @abstractmethod
    def decode_refresh_token(self, token: str) -> dict[str, Any]:
        """Decode and validate a refresh token, returning the payload."""
