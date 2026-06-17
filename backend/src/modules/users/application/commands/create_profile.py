import uuid
from dataclasses import dataclass

from modules.users.application.ports.user_repository import UserRepository
from modules.users.domain.entities.user_profile import UserProfile
from shared.application.ports.unit_of_work import AbstractUnitOfWork


@dataclass(frozen=True)
class CreateProfileCommand:
    account_id: uuid.UUID
    first_name: str
    last_name: str
    preferred_language: str = "en"


class CreateProfileHandler:
    def __init__(self, user_repo: UserRepository, uow: AbstractUnitOfWork) -> None:
        self._user_repo = user_repo
        self._uow = uow

    async def handle(self, command: CreateProfileCommand) -> uuid.UUID:
        existing = await self._user_repo.get_by_account_id(command.account_id)
        if existing:
            return existing.id

        profile = UserProfile.create(
            account_id=command.account_id,
            first_name=command.first_name,
            last_name=command.last_name,
            preferred_language=command.preferred_language,
        )

        async with self._uow:
            await self._user_repo.add(profile)
            await self._uow.commit()

        return profile.id


def parse_names_from_email(email: str) -> tuple[str, str]:
    """Parse first name and last name from email local part."""
    local_part = email.split("@", maxsplit=1)[0]
    parts = local_part.split(".")
    if len(parts) >= 2:
        return parts[0].capitalize(), parts[1].capitalize()
    return local_part.capitalize(), "User"
