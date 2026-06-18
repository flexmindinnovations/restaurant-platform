import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from modules.users.domain.events.profile_events import ProfileCreated, ProfileUpdated
from shared.domain.entity import AggregateRoot


@dataclass
class UserProfile(AggregateRoot):
    account_id: uuid.UUID = None  # type: ignore[assignment]
    first_name: str = ""
    last_name: str = ""
    display_name: str | None = None
    avatar_url: str | None = None
    preferred_language: str = "en"

    @classmethod
    def create(
        cls,
        account_id: uuid.UUID,
        first_name: str,
        last_name: str,
        display_name: str | None = None,
        avatar_url: str | None = None,
        preferred_language: str = "en",
    ) -> "UserProfile":
        profile_id = uuid.uuid4()
        profile = cls(
            id=profile_id,
            account_id=account_id,
            first_name=first_name,
            last_name=last_name,
            display_name=display_name or f"{first_name} {last_name}",
            avatar_url=avatar_url,
            preferred_language=preferred_language,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        profile.register_event(
            ProfileCreated(
                aggregate_id=profile_id,
                account_id=account_id,
                first_name=first_name,
                last_name=last_name,
            )
        )
        return profile

    def update_profile(
        self,
        first_name: str | None = None,
        last_name: str | None = None,
        display_name: str | None = None,
        avatar_url: str | None = None,
        preferred_language: str | None = None,
    ) -> None:
        if first_name is not None:
            self.first_name = first_name
        if last_name is not None:
            self.last_name = last_name
        if display_name is not None:
            self.display_name = display_name
        if avatar_url is not None:
            self.avatar_url = avatar_url
        if preferred_language is not None:
            self.preferred_language = preferred_language
        self.updated_at = datetime.now(UTC)
        self.register_event(ProfileUpdated(aggregate_id=self.id))
