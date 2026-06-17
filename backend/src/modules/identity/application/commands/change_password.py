import uuid
from dataclasses import dataclass

from modules.identity.application.ports.account_repository import AccountRepository
from modules.identity.application.ports.password_hasher import PasswordHasher
from modules.identity.domain.value_objects.password import Password
from shared.domain.exceptions import ValidationException
from shared.application.ports.unit_of_work import AbstractUnitOfWork


@dataclass(frozen=True)
class ChangePasswordCommand:
    account_id: uuid.UUID
    old_password: str
    new_password: str


class ChangePasswordHandler:
    def __init__(
        self,
        account_repo: AccountRepository,
        password_hasher: PasswordHasher,
        uow: AbstractUnitOfWork,
    ) -> None:
        self._account_repo = account_repo
        self._password_hasher = password_hasher
        self._uow = uow

    async def handle(self, command: ChangePasswordCommand) -> None:
        account = await self._account_repo.get_by_id(command.account_id)
        if not account:
            raise ValidationException("Account not found")

        # Verify old password
        if not self._password_hasher.verify(command.old_password, account.password_hash):
            raise ValidationException("Invalid current password")

        # Create Password value object (validates complexity)
        new_password_vo = Password.create(
            command.new_password,
            self._password_hasher.hash
        )

        account.change_password(new_password_vo)

        async with self._uow:
            await self._account_repo.update(account)
            self._uow.register_aggregate(account)
            await self._uow.commit()
