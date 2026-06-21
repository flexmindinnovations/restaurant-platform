import hashlib
import time
from dataclasses import dataclass

from modules.identity.application.ports.account_repository import AccountRepository
from modules.identity.application.ports.password_hasher import PasswordHasher
from modules.identity.application.ports.token_service import TokenService
from modules.identity.domain.value_objects.email import Email
from shared.application.ports.unit_of_work import AbstractUnitOfWork
from shared.domain.exceptions import AuthenticationException


@dataclass(frozen=True)
class LoginCommand:
    email: str
    password: str


@dataclass(frozen=True)
class LoginResult:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LoginHandler:
    def __init__(
        self,
        account_repo: AccountRepository,
        password_hasher: PasswordHasher,
        token_service: TokenService,
        uow: AbstractUnitOfWork,
    ) -> None:
        self._account_repo = account_repo
        self._password_hasher = password_hasher
        self._token_service = token_service
        self._uow = uow

    async def handle(self, command: LoginCommand) -> LoginResult:
        email_vo = Email(command.email)
        account = await self._account_repo.get_by_email(email_vo)
        if not account:
            raise AuthenticationException("Invalid credentials")

        # Verify password
        if not self._password_hasher.verify(command.password, account.password_hash):
            raise AuthenticationException("Invalid credentials")

        if not account.is_active:
            raise AuthenticationException("Account is inactive")

        if not account.is_verified:
            raise AuthenticationException("Email not verified")

        # Generate tokens
        roles_list = [r.value for r in account.roles]
        access_token = self._token_service.generate_access_token(account.id, roles_list)
        refresh_token = self._token_service.generate_refresh_token(account.id)

        # Hash refresh token for DB storage (sha256)
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()

        # Calculate expiry (7 days from now)
        expires_at = time.time() + (7 * 24 * 60 * 60)

        async with self._uow:
            await self._account_repo.add_refresh_token(
                token_hash=token_hash,
                account_id=account.id,
                expires_at=expires_at,
            )
            await self._uow.commit()

        return LoginResult(
            access_token=access_token,
            refresh_token=refresh_token,
        )
