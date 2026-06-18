import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.identity.application.ports.account_repository import AccountRepository
from modules.identity.domain.entities.account import Account
from modules.identity.domain.value_objects.email import Email
from modules.identity.domain.value_objects.phone_number import PhoneNumber
from modules.identity.domain.value_objects.role import Role
from modules.identity.infrastructure.models.account_model import AccountModel, RefreshTokenModel


class SqlAlchemyAccountRepository(AccountRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, account: Account) -> None:
        model = AccountModel(
            id=account.id,
            email=account.email.value,
            password_hash=account.password_hash,
            phone_number=account.phone_number.value if account.phone_number else None,
            is_verified=account.is_verified,
            is_active=account.is_active,
            verification_token=account.verification_token,
            roles=[r.value for r in account.roles],
            created_at=account.created_at,
            updated_at=account.updated_at,
        )
        self._session.add(model)

    async def get_by_id(self, account_id: uuid.UUID) -> Account | None:
        result = await self._session.execute(select(AccountModel).where(AccountModel.id == account_id))
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_domain(model)

    async def get_by_email(self, email: Email) -> Account | None:
        result = await self._session.execute(select(AccountModel).where(AccountModel.email == email.value))
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_domain(model)

    async def get_by_verification_token(self, token: str) -> Account | None:
        result = await self._session.execute(select(AccountModel).where(AccountModel.verification_token == token))
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_domain(model)

    async def get_by_reset_token(self, token: str) -> Account | None:
        result = await self._session.execute(select(AccountModel).where(AccountModel.reset_token == token))
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_domain(model)

    async def update(self, account: Account) -> None:
        result = await self._session.execute(select(AccountModel).where(AccountModel.id == account.id))
        model = result.scalar_one_or_none()
        if model:
            model.email = account.email.value
            model.password_hash = account.password_hash
            model.phone_number = account.phone_number.value if account.phone_number else None
            model.is_verified = account.is_verified
            model.is_active = account.is_active
            model.verification_token = account.verification_token
            model.reset_token = account.reset_token
            model.reset_token_expires_at = account.reset_token_expires_at
            model.roles = [r.value for r in account.roles]
            model.updated_at = account.updated_at

    async def add_refresh_token(self, token_hash: str, account_id: uuid.UUID, expires_at: float) -> None:
        expires_datetime = datetime.fromtimestamp(expires_at, tz=UTC)
        model = RefreshTokenModel(
            token_hash=token_hash,
            account_id=account_id,
            expires_at=expires_datetime,
            is_revoked=False,
        )
        self._session.add(model)

    async def get_refresh_token(self, token_hash: str) -> dict[str, Any] | None:
        result = await self._session.execute(
            select(RefreshTokenModel).where(RefreshTokenModel.token_hash == token_hash)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return {
            "token_hash": model.token_hash,
            "account_id": model.account_id,
            "expires_at": model.expires_at.timestamp(),
            "is_revoked": model.is_revoked,
        }

    async def revoke_refresh_token(self, token_hash: str) -> None:
        result = await self._session.execute(
            select(RefreshTokenModel).where(RefreshTokenModel.token_hash == token_hash)
        )
        model = result.scalar_one_or_none()
        if model:
            model.is_revoked = True

    def _to_domain(self, model: AccountModel) -> Account:
        return Account(
            id=model.id,
            email=Email(model.email),
            password_hash=model.password_hash,
            phone_number=PhoneNumber(model.phone_number) if model.phone_number else None,
            is_verified=model.is_verified,
            is_active=model.is_active,
            verification_token=model.verification_token,
            reset_token=model.reset_token,
            reset_token_expires_at=model.reset_token_expires_at,
            roles=[Role(r) for r in model.roles],
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
