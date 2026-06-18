from dataclasses import dataclass

from modules.identity.application.ports.account_repository import AccountRepository
from modules.identity.domain.value_objects.email import Email
from shared.application.ports.unit_of_work import AbstractUnitOfWork
from shared.domain.exceptions import ValidationException


@dataclass(frozen=True)
class VerifyEmailCommand:
    email: str
    token: str


class VerifyEmailHandler:
    def __init__(self, account_repo: AccountRepository, uow: AbstractUnitOfWork) -> None:
        self._account_repo = account_repo
        self._uow = uow

    async def handle(self, command: VerifyEmailCommand) -> None:
        email_vo = Email(command.email)
        account = await self._account_repo.get_by_email(email_vo)
        if not account:
            raise ValidationException("Account not found")

        account.verify_email(command.token)

        async with self._uow:
            await self._account_repo.update(account)
            self._uow.register_aggregate(account)
            await self._uow.commit()
