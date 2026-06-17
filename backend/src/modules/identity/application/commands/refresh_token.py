import hashlib
import time
import uuid
from dataclasses import dataclass

from modules.identity.application.ports.account_repository import AccountRepository
from modules.identity.application.ports.token_service import TokenService
from shared.domain.exceptions import ValidationException
from shared.application.ports.unit_of_work import AbstractUnitOfWork


@dataclass(frozen=True)
class RefreshTokenCommand:
    refresh_token: str


@dataclass(frozen=True)
class RefreshTokenResult:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenHandler:
    def __init__(
        self,
        account_repo: AccountRepository,
        token_service: TokenService,
        uow: AbstractUnitOfWork,
    ) -> None:
        self._account_repo = account_repo
        self._token_service = token_service
        self._uow = uow

    async def handle(self, command: RefreshTokenCommand) -> RefreshTokenResult:
        try:
            payload = self._token_service.decode_refresh_token(command.refresh_token)
        except Exception:
            raise ValidationException("Invalid refresh token")

        # Hash refresh token to check in DB
        old_token_hash = hashlib.sha256(command.refresh_token.encode()).hexdigest()
        token_record = await self._account_repo.get_refresh_token(old_token_hash)
        
        expires_at = token_record.get("expires_at") if token_record else None
        if not token_record or token_record.get("is_revoked") or expires_at is None or float(expires_at) < time.time():
            raise ValidationException("Invalid refresh token")

        account_id = uuid.UUID(payload["sub"])
        account = await self._account_repo.get_by_id(account_id)
        if not account or not account.is_active:
            raise ValidationException("Account is inactive or not found")

        # Generate new tokens
        roles_list = [r.value for r in account.roles]
        new_access_token = self._token_service.generate_access_token(account.id, roles_list)
        new_refresh_token = self._token_service.generate_refresh_token(account.id)

        # Hash new refresh token
        new_token_hash = hashlib.sha256(new_refresh_token.encode()).hexdigest()
        new_expires_at = time.time() + (7 * 24 * 60 * 60)

        async with self._uow:
            # Revoke old token
            await self._account_repo.revoke_refresh_token(old_token_hash)
            # Add new token
            await self._account_repo.add_refresh_token(
                token_hash=new_token_hash,
                account_id=account.id,
                expires_at=new_expires_at,
            )
            await self._uow.commit()

        return RefreshTokenResult(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
        )
