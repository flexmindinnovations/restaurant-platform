import uuid
from dataclasses import dataclass
from datetime import datetime

from modules.identity.application.ports.account_repository import AccountRepository
from shared.domain.exceptions import NotFoundException


@dataclass(frozen=True)
class GetAccountQuery:
    account_id: uuid.UUID


@dataclass(frozen=True)
class AccountDTO:
    id: uuid.UUID
    email: str
    phone_number: str | None
    is_verified: bool
    is_active: bool
    roles: list[str]
    created_at: datetime
    updated_at: datetime


class GetAccountHandler:
    def __init__(self, account_repo: AccountRepository) -> None:
        self._account_repo = account_repo

    async def handle(self, query: GetAccountQuery) -> AccountDTO:
        account = await self._account_repo.get_by_id(query.account_id)
        if not account:
            raise NotFoundException("Account not found")

        return AccountDTO(
            id=account.id,
            email=account.email.value,
            phone_number=account.phone_number.value if account.phone_number else None,
            is_verified=account.is_verified,
            is_active=account.is_active,
            roles=[r.value for r in account.roles],
            created_at=account.created_at,
            updated_at=account.updated_at,
        )
