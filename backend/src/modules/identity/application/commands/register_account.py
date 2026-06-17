import secrets
import uuid
from dataclasses import dataclass

from modules.identity.application.ports.account_repository import AccountRepository
from modules.identity.application.ports.email_sender import EmailSender
from modules.identity.application.ports.password_hasher import PasswordHasher
from modules.identity.domain.entities.account import Account
from modules.identity.domain.value_objects.email import Email
from modules.identity.domain.value_objects.password import Password
from modules.identity.domain.value_objects.phone_number import PhoneNumber
from modules.identity.domain.value_objects.role import Role
from shared.domain.exceptions import ValidationException
from shared.application.ports.unit_of_work import AbstractUnitOfWork


@dataclass(frozen=True)
class RegisterAccountCommand:
    email: str
    password: str
    phone_number: str | None = None
    roles: list[str] | None = None


class RegisterAccountHandler:
    def __init__(
        self,
        account_repo: AccountRepository,
        password_hasher: PasswordHasher,
        email_sender: EmailSender,
        uow: AbstractUnitOfWork,
    ) -> None:
        self._account_repo = account_repo
        self._password_hasher = password_hasher
        self._email_sender = email_sender
        self._uow = uow

    async def handle(self, command: RegisterAccountCommand) -> uuid.UUID:
        email_vo = Email(command.email)

        # Check if email is already taken
        existing = await self._account_repo.get_by_email(email_vo)
        if existing:
            raise ValidationException("Email is already registered")

        phone_vo = PhoneNumber(command.phone_number) if command.phone_number else None

        # Parse roles
        roles_vo: list[Role] = []
        if command.roles:
            for role_str in command.roles:
                try:
                    roles_vo.append(Role(role_str))
                except ValueError:
                    raise ValidationException(f"Invalid role: {role_str}")
        else:
            roles_vo = [Role.CUSTOMER]

        # Generate verification token
        verification_token = secrets.token_urlsafe(32)

        # Create Password value object (uses hasher callback)
        password_vo = Password.create(
            command.password,
            self._password_hasher.hash
        )

        # Register aggregate
        account = Account.register(
            email=email_vo,
            password=password_vo,
            phone_number=phone_vo,
            verification_token=verification_token,
            roles=roles_vo,
        )

        async with self._uow:
            await self._account_repo.add(account)
            self._uow.register_aggregate(account)
            await self._uow.commit()

        # Send verification email in background/asynchronously
        try:
            await self._email_sender.send_verification_email(command.email, verification_token)
        except Exception:
            # Don't fail the registration if sending email fails, but log it or handle it
            pass

        return account.id
