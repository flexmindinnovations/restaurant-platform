import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from modules.identity.application.ports.account_repository import AccountRepository
from modules.identity.application.ports.email_sender import EmailSender
from modules.identity.domain.value_objects.email import Email
from shared.application.ports.unit_of_work import AbstractUnitOfWork

RESET_TOKEN_EXPIRY_HOURS = 1


@dataclass(frozen=True)
class ForgotPasswordCommand:
    email: str


class ForgotPasswordHandler:
    def __init__(
        self,
        account_repo: AccountRepository,
        email_sender: EmailSender,
        uow: AbstractUnitOfWork,
    ) -> None:
        self._account_repo = account_repo
        self._email_sender = email_sender
        self._uow = uow

    async def handle(self, command: ForgotPasswordCommand) -> None:
        email_vo = Email(command.email)
        account = await self._account_repo.get_by_email(email_vo)
        if not account:
            return

        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(UTC) + timedelta(hours=RESET_TOKEN_EXPIRY_HOURS)
        account.request_password_reset(token, expires_at)

        async with self._uow:
            await self._account_repo.update(account)
            await self._uow.commit()

        await self._email_sender.send_password_reset_email(command.email, token)
