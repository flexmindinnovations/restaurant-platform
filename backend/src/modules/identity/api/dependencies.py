from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.dependencies import get_db_session
from modules.identity.application.commands.change_password import ChangePasswordHandler
from modules.identity.application.commands.forgot_password import ForgotPasswordHandler
from modules.identity.application.commands.register_account import RegisterAccountHandler
from modules.identity.application.commands.reset_password import ResetPasswordHandler
from modules.identity.application.ports.account_repository import AccountRepository
from modules.identity.application.ports.email_sender import EmailSender
from modules.identity.application.ports.password_hasher import PasswordHasher
from modules.identity.application.ports.token_service import TokenService
from modules.identity.application.queries.get_account import GetAccountHandler
from modules.identity.application.services.auth_service import AuthService
from modules.identity.infrastructure.adapters.bcrypt_password_hasher import BcryptPasswordHasher
from modules.identity.infrastructure.adapters.jwt_token_service import JwtTokenService
from modules.identity.infrastructure.adapters.smtp_email_sender import SmtpEmailSender
from modules.identity.infrastructure.repositories.account_repository import SqlAlchemyAccountRepository
from shared.infrastructure.event_bus import get_event_bus
from shared.infrastructure.unit_of_work import SqlAlchemyUnitOfWork


def get_account_repository(session: AsyncSession = Depends(get_db_session)) -> AccountRepository:
    return SqlAlchemyAccountRepository(session)


def get_password_hasher() -> PasswordHasher:
    return BcryptPasswordHasher()


def get_token_service() -> TokenService:
    settings = get_settings()
    return JwtTokenService(
        secret_key=settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
        access_expire_minutes=settings.jwt_access_token_expire_minutes,
        refresh_expire_days=settings.jwt_refresh_token_expire_days,
    )


def get_email_sender() -> EmailSender:
    return SmtpEmailSender()


def get_uow(session: AsyncSession = Depends(get_db_session)) -> SqlAlchemyUnitOfWork:
    return SqlAlchemyUnitOfWork(session, get_event_bus())


def get_auth_service(
    account_repo: AccountRepository = Depends(get_account_repository),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
    token_service: TokenService = Depends(get_token_service),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> AuthService:
    return AuthService(account_repo, password_hasher, token_service, uow)


def get_register_handler(
    account_repo: AccountRepository = Depends(get_account_repository),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
    email_sender: EmailSender = Depends(get_email_sender),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> RegisterAccountHandler:
    return RegisterAccountHandler(account_repo, password_hasher, email_sender, uow)


def get_change_password_handler(
    account_repo: AccountRepository = Depends(get_account_repository),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> ChangePasswordHandler:
    return ChangePasswordHandler(account_repo, password_hasher, uow)


def get_forgot_password_handler(
    account_repo: AccountRepository = Depends(get_account_repository),
    email_sender: EmailSender = Depends(get_email_sender),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> ForgotPasswordHandler:
    return ForgotPasswordHandler(account_repo, email_sender, uow)


def get_reset_password_handler(
    account_repo: AccountRepository = Depends(get_account_repository),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> ResetPasswordHandler:
    return ResetPasswordHandler(account_repo, password_hasher, uow)


def get_account_query_handler(
    account_repo: AccountRepository = Depends(get_account_repository),
) -> GetAccountHandler:
    return GetAccountHandler(account_repo)
