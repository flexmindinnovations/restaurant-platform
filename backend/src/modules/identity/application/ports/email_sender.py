from abc import ABC, abstractmethod


class EmailSender(ABC):
    @abstractmethod
    async def send_verification_email(self, email: str, token: str) -> None:
        """Send a verification link containing the token to the user's email."""

    @abstractmethod
    async def send_password_reset_email(self, email: str, token: str) -> None:
        """Send a password reset link containing the token to the user's email."""
