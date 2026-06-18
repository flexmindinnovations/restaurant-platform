import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.users.application.ports.user_repository import UserRepository
from modules.users.domain.entities.user_profile import UserProfile
from modules.users.infrastructure.models.profile_model import ProfileModel


class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, profile: UserProfile) -> None:
        model = ProfileModel(
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
        self._session.add(model)

    async def get_by_id(self, profile_id: uuid.UUID) -> UserProfile | None:
        result = await self._session.execute(select(ProfileModel).where(ProfileModel.id == profile_id))
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_domain(model)

    async def get_by_account_id(self, account_id: uuid.UUID) -> UserProfile | None:
        result = await self._session.execute(select(ProfileModel).where(ProfileModel.account_id == account_id))
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_domain(model)

    async def update(self, profile: UserProfile) -> None:
        result = await self._session.execute(select(ProfileModel).where(ProfileModel.id == profile.id))
        model = result.scalar_one_or_none()
        if model:
            model.first_name = profile.first_name
            model.last_name = profile.last_name
            model.display_name = profile.display_name
            model.avatar_url = profile.avatar_url
            model.preferred_language = profile.preferred_language
            model.updated_at = profile.updated_at

    def _to_domain(self, model: ProfileModel) -> UserProfile:
        return UserProfile(
            id=model.id,
            account_id=model.account_id,
            first_name=model.first_name,
            last_name=model.last_name,
            display_name=model.display_name,
            avatar_url=model.avatar_url,
            preferred_language=model.preferred_language,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
