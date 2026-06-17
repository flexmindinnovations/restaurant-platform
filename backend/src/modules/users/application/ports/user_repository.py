import uuid
from abc import ABC, abstractmethod

from modules.users.domain.entities.user_profile import UserProfile


class UserRepository(ABC):
    @abstractmethod
    async def add(self, profile: UserProfile) -> None:
        """Add a new user profile."""

    @abstractmethod
    async def get_by_id(self, profile_id: uuid.UUID) -> UserProfile | None:
        """Retrieve a profile by its ID."""

    @abstractmethod
    async def get_by_account_id(self, account_id: uuid.UUID) -> UserProfile | None:
        """Retrieve a profile by its associated Account ID."""

    @abstractmethod
    async def update(self, profile: UserProfile) -> None:
        """Update an existing profile."""
