import time
import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from modules.identity.application.commands.change_password import ChangePasswordCommand, ChangePasswordHandler
from modules.identity.application.commands.forgot_password import ForgotPasswordCommand, ForgotPasswordHandler
from modules.identity.application.commands.login import LoginCommand, LoginHandler
from modules.identity.application.commands.refresh_token import RefreshTokenCommand, RefreshTokenHandler
from modules.identity.application.commands.register_account import RegisterAccountCommand, RegisterAccountHandler
from modules.identity.application.commands.reset_password import ResetPasswordCommand, ResetPasswordHandler
from modules.identity.application.commands.verify_email import VerifyEmailCommand, VerifyEmailHandler
from modules.identity.application.queries.get_account import GetAccountHandler, GetAccountQuery
from modules.identity.domain.entities.account import Account
from modules.identity.domain.value_objects.email import Email
from modules.identity.domain.value_objects.role import Role
from shared.domain.exceptions import AuthenticationException, NotFoundException, ValidationException


def _make_account(
    *,
    email: str = "user@example.com",
    verified: bool = True,
    active: bool = True,
    password_hash: str = "hashed_SecurePass1!",
    roles: list[Role] | None = None,
    reset_token: str | None = None,
    reset_token_expires_at: datetime | None = None,
) -> Account:
    return Account(
        id=uuid.uuid4(),
        email=Email(email),
        password_hash=password_hash,
        is_verified=verified,
        is_active=active,
        roles=roles or [Role.CUSTOMER],
        reset_token=reset_token,
        reset_token_expires_at=reset_token_expires_at,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


def _mock_uow() -> AsyncMock:
    uow = AsyncMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)
    uow._aggregates = []
    uow.register_aggregate = MagicMock(side_effect=lambda agg: uow._aggregates.append(agg))
    return uow


def _mock_repo() -> AsyncMock:
    return AsyncMock()


def _mock_hasher() -> MagicMock:
    hasher = MagicMock()
    hasher.hash = MagicMock(side_effect=lambda p: f"hashed_{p}")
    hasher.verify = MagicMock(return_value=True)
    return hasher


def _mock_email_sender() -> AsyncMock:
    return AsyncMock()


def _mock_token_service() -> MagicMock:
    ts = MagicMock()
    ts.generate_access_token = MagicMock(return_value="access_token_123")
    ts.generate_refresh_token = MagicMock(return_value="refresh_token_456")
    ts.decode_refresh_token = MagicMock(return_value={"sub": str(uuid.uuid4())})
    return ts


# ---------------------------------------------------------------------------
# RegisterAccountHandler
# ---------------------------------------------------------------------------


class TestRegisterAccountHandler:
    @pytest.mark.asyncio
    async def test_register_new_account(self) -> None:
        repo = _mock_repo()
        repo.get_by_email.return_value = None
        hasher = _mock_hasher()
        email_sender = _mock_email_sender()
        uow = _mock_uow()

        handler = RegisterAccountHandler(repo, hasher, email_sender, uow)
        cmd = RegisterAccountCommand(email="new@example.com", password="SecurePass1!")

        result = await handler.handle(cmd)

        assert isinstance(result, uuid.UUID)
        repo.add.assert_awaited_once()
        uow.commit.assert_awaited_once()
        email_sender.send_verification_email.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_register_duplicate_email_raises(self) -> None:
        repo = _mock_repo()
        repo.get_by_email.return_value = _make_account()
        uow = _mock_uow()

        handler = RegisterAccountHandler(repo, _mock_hasher(), _mock_email_sender(), uow)
        cmd = RegisterAccountCommand(email="user@example.com", password="SecurePass1!")

        with pytest.raises(ValidationException, match="already registered"):
            await handler.handle(cmd)
        repo.add.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_register_with_custom_roles(self) -> None:
        repo = _mock_repo()
        repo.get_by_email.return_value = None
        uow = _mock_uow()

        handler = RegisterAccountHandler(repo, _mock_hasher(), _mock_email_sender(), uow)
        cmd = RegisterAccountCommand(
            email="owner@example.com",
            password="SecurePass1!",
            roles=["RESTAURANT_OWNER"],
        )

        result = await handler.handle(cmd)
        assert isinstance(result, uuid.UUID)

    @pytest.mark.asyncio
    async def test_register_with_invalid_role_raises(self) -> None:
        repo = _mock_repo()
        repo.get_by_email.return_value = None
        uow = _mock_uow()

        handler = RegisterAccountHandler(repo, _mock_hasher(), _mock_email_sender(), uow)
        cmd = RegisterAccountCommand(
            email="owner@example.com",
            password="SecurePass1!",
            roles=["INVALID_ROLE"],
        )

        with pytest.raises(ValidationException, match="Invalid role"):
            await handler.handle(cmd)


# ---------------------------------------------------------------------------
# LoginHandler
# ---------------------------------------------------------------------------


class TestLoginHandler:
    @pytest.mark.asyncio
    async def test_login_success(self) -> None:
        account = _make_account(verified=True, active=True)
        repo = _mock_repo()
        repo.get_by_email.return_value = account
        hasher = _mock_hasher()
        hasher.verify.return_value = True
        token_service = _mock_token_service()
        uow = _mock_uow()

        handler = LoginHandler(repo, hasher, token_service, uow)
        result = await handler.handle(LoginCommand(email="user@example.com", password="SecurePass1!"))

        assert result.access_token == "access_token_123"
        assert result.refresh_token == "refresh_token_456"
        repo.add_refresh_token.assert_awaited_once()
        uow.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_login_wrong_password(self) -> None:
        repo = _mock_repo()
        repo.get_by_email.return_value = _make_account()
        hasher = _mock_hasher()
        hasher.verify.return_value = False
        uow = _mock_uow()

        handler = LoginHandler(repo, hasher, _mock_token_service(), uow)

        with pytest.raises(AuthenticationException, match="Invalid credentials"):
            await handler.handle(LoginCommand(email="user@example.com", password="wrong"))

    @pytest.mark.asyncio
    async def test_login_nonexistent_email(self) -> None:
        repo = _mock_repo()
        repo.get_by_email.return_value = None
        uow = _mock_uow()

        handler = LoginHandler(repo, _mock_hasher(), _mock_token_service(), uow)

        with pytest.raises(AuthenticationException, match="Invalid credentials"):
            await handler.handle(LoginCommand(email="gone@example.com", password="pass"))

    @pytest.mark.asyncio
    async def test_login_inactive_account(self) -> None:
        repo = _mock_repo()
        repo.get_by_email.return_value = _make_account(active=False)
        hasher = _mock_hasher()
        hasher.verify.return_value = True
        uow = _mock_uow()

        handler = LoginHandler(repo, hasher, _mock_token_service(), uow)

        with pytest.raises(AuthenticationException, match="inactive"):
            await handler.handle(LoginCommand(email="user@example.com", password="SecurePass1!"))

    @pytest.mark.asyncio
    async def test_login_unverified_account(self) -> None:
        repo = _mock_repo()
        repo.get_by_email.return_value = _make_account(verified=False)
        hasher = _mock_hasher()
        hasher.verify.return_value = True
        uow = _mock_uow()

        handler = LoginHandler(repo, hasher, _mock_token_service(), uow)

        with pytest.raises(AuthenticationException, match="not verified"):
            await handler.handle(LoginCommand(email="user@example.com", password="SecurePass1!"))


# ---------------------------------------------------------------------------
# VerifyEmailHandler
# ---------------------------------------------------------------------------


class TestVerifyEmailHandler:
    @pytest.mark.asyncio
    async def test_verify_email_success(self) -> None:
        account = _make_account(verified=False)
        account.verification_token = "valid_token"
        repo = _mock_repo()
        repo.get_by_email.return_value = account
        uow = _mock_uow()

        handler = VerifyEmailHandler(repo, uow)
        await handler.handle(VerifyEmailCommand(email="user@example.com", token="valid_token"))

        assert account.is_verified is True
        repo.update.assert_awaited_once()
        uow.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_verify_email_wrong_token(self) -> None:
        account = _make_account(verified=False)
        account.verification_token = "valid_token"
        repo = _mock_repo()
        repo.get_by_email.return_value = account
        uow = _mock_uow()

        handler = VerifyEmailHandler(repo, uow)

        with pytest.raises(ValidationException, match="Invalid verification token"):
            await handler.handle(VerifyEmailCommand(email="user@example.com", token="bad"))

    @pytest.mark.asyncio
    async def test_verify_email_account_not_found(self) -> None:
        repo = _mock_repo()
        repo.get_by_email.return_value = None
        uow = _mock_uow()

        handler = VerifyEmailHandler(repo, uow)

        with pytest.raises(ValidationException, match="Account not found"):
            await handler.handle(VerifyEmailCommand(email="missing@example.com", token="t"))


# ---------------------------------------------------------------------------
# ChangePasswordHandler
# ---------------------------------------------------------------------------


class TestChangePasswordHandler:
    @pytest.mark.asyncio
    async def test_change_password_success(self) -> None:
        account = _make_account()
        repo = _mock_repo()
        repo.get_by_id.return_value = account
        hasher = _mock_hasher()
        hasher.verify.return_value = True
        uow = _mock_uow()

        handler = ChangePasswordHandler(repo, hasher, uow)
        await handler.handle(
            ChangePasswordCommand(
                account_id=account.id,
                old_password="OldSecure1!",
                new_password="NewSecure1!",
            )
        )

        assert account.password_hash == "hashed_NewSecure1!"
        repo.update.assert_awaited_once()
        uow.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_change_password_wrong_old(self) -> None:
        account = _make_account()
        repo = _mock_repo()
        repo.get_by_id.return_value = account
        hasher = _mock_hasher()
        hasher.verify.return_value = False
        uow = _mock_uow()

        handler = ChangePasswordHandler(repo, hasher, uow)

        with pytest.raises(ValidationException, match="Invalid current password"):
            await handler.handle(
                ChangePasswordCommand(
                    account_id=account.id,
                    old_password="wrong",
                    new_password="NewSecure1!",
                )
            )

    @pytest.mark.asyncio
    async def test_change_password_account_not_found(self) -> None:
        repo = _mock_repo()
        repo.get_by_id.return_value = None
        uow = _mock_uow()

        handler = ChangePasswordHandler(repo, _mock_hasher(), uow)

        with pytest.raises(ValidationException, match="Account not found"):
            await handler.handle(
                ChangePasswordCommand(
                    account_id=uuid.uuid4(),
                    old_password="x",
                    new_password="NewSecure1!",
                )
            )


# ---------------------------------------------------------------------------
# ForgotPasswordHandler
# ---------------------------------------------------------------------------


class TestForgotPasswordHandler:
    @pytest.mark.asyncio
    async def test_forgot_password_sends_email(self) -> None:
        account = _make_account()
        repo = _mock_repo()
        repo.get_by_email.return_value = account
        email_sender = _mock_email_sender()
        uow = _mock_uow()

        handler = ForgotPasswordHandler(repo, email_sender, uow)
        await handler.handle(ForgotPasswordCommand(email="user@example.com"))

        assert account.reset_token is not None
        assert account.reset_token_expires_at is not None
        repo.update.assert_awaited_once()
        uow.commit.assert_awaited_once()
        email_sender.send_password_reset_email.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_forgot_password_unknown_email_silent(self) -> None:
        repo = _mock_repo()
        repo.get_by_email.return_value = None
        email_sender = _mock_email_sender()
        uow = _mock_uow()

        handler = ForgotPasswordHandler(repo, email_sender, uow)
        await handler.handle(ForgotPasswordCommand(email="nope@example.com"))

        repo.update.assert_not_awaited()
        email_sender.send_password_reset_email.assert_not_awaited()


# ---------------------------------------------------------------------------
# ResetPasswordHandler
# ---------------------------------------------------------------------------


class TestResetPasswordHandler:
    @pytest.mark.asyncio
    async def test_reset_password_success(self) -> None:
        account = _make_account(
            reset_token="valid_reset",
            reset_token_expires_at=datetime.now(UTC) + timedelta(hours=1),
        )
        repo = _mock_repo()
        repo.get_by_reset_token.return_value = account
        hasher = _mock_hasher()
        uow = _mock_uow()

        handler = ResetPasswordHandler(repo, hasher, uow)
        await handler.handle(ResetPasswordCommand(token="valid_reset", new_password="NewSecure1!"))

        assert account.password_hash == "hashed_NewSecure1!"
        assert account.reset_token is None
        repo.update.assert_awaited_once()
        uow.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_reset_password_invalid_token(self) -> None:
        repo = _mock_repo()
        repo.get_by_reset_token.return_value = None
        uow = _mock_uow()

        handler = ResetPasswordHandler(repo, _mock_hasher(), uow)

        with pytest.raises(ValidationException, match="Invalid or expired token"):
            await handler.handle(ResetPasswordCommand(token="bad", new_password="NewSecure1!"))

    @pytest.mark.asyncio
    async def test_reset_password_empty_token(self) -> None:
        repo = _mock_repo()
        uow = _mock_uow()

        handler = ResetPasswordHandler(repo, _mock_hasher(), uow)

        with pytest.raises(ValidationException, match="Invalid token"):
            await handler.handle(ResetPasswordCommand(token="", new_password="NewSecure1!"))


# ---------------------------------------------------------------------------
# RefreshTokenHandler
# ---------------------------------------------------------------------------


class TestRefreshTokenHandler:
    @pytest.mark.asyncio
    async def test_refresh_token_success(self) -> None:
        account = _make_account()
        account_id = account.id
        repo = _mock_repo()
        repo.get_refresh_token.return_value = {
            "account_id": str(account_id),
            "is_revoked": False,
            "expires_at": time.time() + 3600,
        }
        repo.get_by_id.return_value = account
        token_service = _mock_token_service()
        token_service.decode_refresh_token.return_value = {"sub": str(account_id)}
        uow = _mock_uow()

        handler = RefreshTokenHandler(repo, token_service, uow)
        result = await handler.handle(RefreshTokenCommand(refresh_token="old_refresh"))

        assert result.access_token == "access_token_123"
        assert result.refresh_token == "refresh_token_456"
        repo.revoke_refresh_token.assert_awaited_once()
        repo.add_refresh_token.assert_awaited_once()
        uow.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_refresh_token_revoked(self) -> None:
        repo = _mock_repo()
        repo.get_refresh_token.return_value = {
            "is_revoked": True,
            "expires_at": time.time() + 3600,
        }
        token_service = _mock_token_service()
        uow = _mock_uow()

        handler = RefreshTokenHandler(repo, token_service, uow)

        with pytest.raises(ValidationException, match="Invalid refresh token"):
            await handler.handle(RefreshTokenCommand(refresh_token="revoked"))

    @pytest.mark.asyncio
    async def test_refresh_token_expired(self) -> None:
        repo = _mock_repo()
        repo.get_refresh_token.return_value = {
            "is_revoked": False,
            "expires_at": time.time() - 3600,
        }
        token_service = _mock_token_service()
        uow = _mock_uow()

        handler = RefreshTokenHandler(repo, token_service, uow)

        with pytest.raises(ValidationException, match="Invalid refresh token"):
            await handler.handle(RefreshTokenCommand(refresh_token="expired"))


# ---------------------------------------------------------------------------
# GetAccountHandler
# ---------------------------------------------------------------------------


class TestGetAccountHandler:
    @pytest.mark.asyncio
    async def test_get_account_success(self) -> None:
        account = _make_account()
        repo = _mock_repo()
        repo.get_by_id.return_value = account

        handler = GetAccountHandler(repo)
        result = await handler.handle(GetAccountQuery(account_id=account.id))

        assert result.email == "user@example.com"
        assert result.is_verified is True
        assert "CUSTOMER" in result.roles

    @pytest.mark.asyncio
    async def test_get_account_not_found(self) -> None:
        repo = _mock_repo()
        repo.get_by_id.return_value = None

        handler = GetAccountHandler(repo)

        with pytest.raises(NotFoundException, match="Account not found"):
            await handler.handle(GetAccountQuery(account_id=uuid.uuid4()))
