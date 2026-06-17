import uuid
from abc import ABC, abstractmethod
from typing import Any

from modules.identity.domain.entities.account import Account
from modules.identity.domain.value_objects.email import Email


class AccountRepository(ABC):
    @abstractmethod
    async def add(self, account: Account) -> None:
        """Add a new account to the database."""

    @abstractmethod
    async def get_by_id(self, account_id: uuid.UUID) -> Account | None:
        """Retrieve an account by its ID."""

    @abstractmethod
    async def get_by_email(self, email: Email) -> Account | None:
        """Retrieve an account by its email."""

    @abstractmethod
    async def get_by_verification_token(self, token: str) -> Account | None:
        """Retrieve an account by its email verification token."""

    @abstractmethod
    async def get_by_reset_token(self, token: str) -> Account | None:
        """Retrieve an account by its password reset token."""

    @abstractmethod
    async def update(self, account: Account) -> None:
        """Update an existing account."""

    @abstractmethod
    async def add_refresh_token(self, token_hash: str, account_id: uuid.UUID, expires_at: float) -> None:
        """Add a refresh token for an account."""

    @abstractmethod
    async def get_refresh_token(self, token_hash: str) -> dict[str, Any] | None:
        """Retrieve a refresh token record by its hash."""

    @abstractmethod
    async def revoke_refresh_token(self, token_hash: str) -> None:
        """Revoke a refresh token."""
