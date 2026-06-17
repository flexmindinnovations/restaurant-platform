import uuid
from dataclasses import dataclass
from datetime import datetime

from modules.users.application.ports.user_repository import UserRepository
from shared.domain.exceptions import NotFoundException


@dataclass(frozen=True)
class GetProfileQuery:
    account_id: uuid.UUID


@dataclass(frozen=True)
class ProfileDTO:
    id: uuid.UUID
    account_id: uuid.UUID
    first_name: str
    last_name: str
    display_name: str | None
    avatar_url: str | None
    preferred_language: str
    created_at: datetime
    updated_at: datetime


class GetProfileHandler:
    def __init__(self, user_repo: UserRepository) -> None:
        self._user_repo = user_repo

    async def handle(self, query: GetProfileQuery) -> ProfileDTO:
        profile = await self._user_repo.get_by_account_id(query.account_id)
        if not profile:
            raise NotFoundException("Profile not found")

        return ProfileDTO(
            id=profile.id,
            account_id=profile.account_id,
            first_name=profile.first_name,
            last_name=profile.last_name,
            display_name=profile.display_name,
            avatar_url=profile.avatar_url,
            preferred_language=profile.preferred_language,
            created_at=profile.created_at,
            updated_at=profile.updated_at,
        )
