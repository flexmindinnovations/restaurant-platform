from dataclasses import dataclass

from modules.identity.application.ports.account_repository import AccountRepository
from modules.identity.application.ports.password_hasher import PasswordHasher
from modules.identity.domain.value_objects.password import Password
from shared.application.ports.unit_of_work import AbstractUnitOfWork
from shared.domain.exceptions import ValidationException


@dataclass(frozen=True)
class ResetPasswordCommand:
    token: str
    new_password: str


class ResetPasswordHandler:
    def __init__(
        self,
        account_repo: AccountRepository,
        password_hasher: PasswordHasher,
        uow: AbstractUnitOfWork,
    ) -> None:
        self._account_repo = account_repo
        self._password_hasher = password_hasher
        self._uow = uow

    async def handle(self, command: ResetPasswordCommand) -> None:
        if not command.token:
            raise ValidationException("Invalid token")

        account = await self._account_repo.get_by_reset_token(command.token)
        if not account:
            raise ValidationException("Invalid or expired token")

        new_password_vo = Password.create(
            command.new_password,
            self._password_hasher.hash,
        )

        account.reset_password(command.token, new_password_vo)

        async with self._uow:
            await self._account_repo.update(account)
            self._uow.register_aggregate(account)
            await self._uow.commit()
