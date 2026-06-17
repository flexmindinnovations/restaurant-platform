from abc import ABC, abstractmethod


class PasswordHasher(ABC):
    @abstractmethod
    def hash(self, password: str) -> str:
        """Hash a plaintext password."""

    @abstractmethod
    def verify(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash."""
