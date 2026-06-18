import uuid
from dataclasses import dataclass

from modules.users.application.ports.user_repository import UserRepository
from shared.application.ports.unit_of_work import AbstractUnitOfWork
from shared.domain.exceptions import NotFoundException


@dataclass(frozen=True)
class UpdateProfileCommand:
    account_id: uuid.UUID
    first_name: str | None = None
    last_name: str | None = None
    display_name: str | None = None
    avatar_url: str | None = None
    preferred_language: str | None = None


class UpdateProfileHandler:
    def __init__(self, user_repo: UserRepository, uow: AbstractUnitOfWork) -> None:
        self._user_repo = user_repo
        self._uow = uow

    async def handle(self, command: UpdateProfileCommand) -> None:
        profile = await self._user_repo.get_by_account_id(command.account_id)
        if not profile:
            raise NotFoundException("Profile not found")

        profile.update_profile(
            first_name=command.first_name,
            last_name=command.last_name,
            display_name=command.display_name,
            avatar_url=command.avatar_url,
            preferred_language=command.preferred_language,
        )

        async with self._uow:
            await self._user_repo.update(profile)
            await self._uow.commit()
