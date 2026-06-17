import hashlib

from modules.identity.application.commands.login import LoginCommand, LoginHandler, LoginResult
from modules.identity.application.commands.refresh_token import (
    RefreshTokenCommand,
    RefreshTokenHandler,
    RefreshTokenResult,
)
from modules.identity.application.commands.verify_email import VerifyEmailCommand, VerifyEmailHandler
from modules.identity.application.ports.account_repository import AccountRepository
from modules.identity.application.ports.password_hasher import PasswordHasher
from modules.identity.application.ports.token_service import TokenService
from shared.application.ports.unit_of_work import AbstractUnitOfWork


class AuthService:
    def __init__(
        self,
        account_repo: AccountRepository,
        password_hasher: PasswordHasher,
        token_service: TokenService,
        uow: AbstractUnitOfWork,
    ) -> None:
        self._account_repo = account_repo
        self._uow = uow
        self._login_handler = LoginHandler(account_repo, password_hasher, token_service, uow)
        self._refresh_handler = RefreshTokenHandler(account_repo, token_service, uow)
        self._verify_handler = VerifyEmailHandler(account_repo, uow)

    async def login(self, command: LoginCommand) -> LoginResult:
        return await self._login_handler.handle(command)

    async def refresh_token(self, command: RefreshTokenCommand) -> RefreshTokenResult:
        return await self._refresh_handler.handle(command)

    async def verify_email(self, command: VerifyEmailCommand) -> None:
        await self._verify_handler.handle(command)

    async def logout(self, refresh_token: str) -> None:
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()  # noqa: S324
        async with self._uow:
            await self._account_repo.revoke_refresh_token(token_hash)
            await self._uow.commit()
