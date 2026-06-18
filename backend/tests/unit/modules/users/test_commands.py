import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from modules.users.application.commands.create_profile import CreateProfileCommand, CreateProfileHandler
from modules.users.application.commands.update_profile import UpdateProfileCommand, UpdateProfileHandler
from modules.users.application.queries.get_profile import GetProfileHandler, GetProfileQuery
from modules.users.domain.entities.user_profile import UserProfile
from shared.domain.exceptions import NotFoundException


def _make_profile(
    *,
    account_id: uuid.UUID | None = None,
    first_name: str = "John",
    last_name: str = "Doe",
) -> UserProfile:
    return UserProfile(
        id=uuid.uuid4(),
        account_id=account_id or uuid.uuid4(),
        first_name=first_name,
        last_name=last_name,
        display_name=f"{first_name} {last_name}",
        avatar_url=None,
        preferred_language="en",
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


# ---------------------------------------------------------------------------
# CreateProfileHandler
# ---------------------------------------------------------------------------


class TestCreateProfileHandler:
    @pytest.mark.asyncio
    async def test_create_profile_success(self) -> None:
        repo = _mock_repo()
        repo.get_by_account_id.return_value = None
        uow = _mock_uow()

        handler = CreateProfileHandler(repo, uow)
        account_id = uuid.uuid4()
        result = await handler.handle(
            CreateProfileCommand(
                account_id=account_id,
                first_name="Jane",
                last_name="Smith",
            )
        )

        assert isinstance(result, uuid.UUID)
        repo.add.assert_awaited_once()
        uow.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_create_profile_idempotent(self) -> None:
        existing = _make_profile()
        repo = _mock_repo()
        repo.get_by_account_id.return_value = existing
        uow = _mock_uow()

        handler = CreateProfileHandler(repo, uow)
        result = await handler.handle(
            CreateProfileCommand(
                account_id=existing.account_id,
                first_name="Jane",
                last_name="Smith",
            )
        )

        assert result == existing.id
        repo.add.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_create_profile_with_language(self) -> None:
        repo = _mock_repo()
        repo.get_by_account_id.return_value = None
        uow = _mock_uow()

        handler = CreateProfileHandler(repo, uow)
        result = await handler.handle(
            CreateProfileCommand(
                account_id=uuid.uuid4(),
                first_name="Pierre",
                last_name="Dupont",
                preferred_language="fr",
            )
        )

        assert isinstance(result, uuid.UUID)
        added_profile = repo.add.call_args[0][0]
        assert added_profile.preferred_language == "fr"


# ---------------------------------------------------------------------------
# UpdateProfileHandler
# ---------------------------------------------------------------------------


class TestUpdateProfileHandler:
    @pytest.mark.asyncio
    async def test_update_profile_success(self) -> None:
        profile = _make_profile()
        repo = _mock_repo()
        repo.get_by_account_id.return_value = profile
        uow = _mock_uow()

        handler = UpdateProfileHandler(repo, uow)
        await handler.handle(
            UpdateProfileCommand(
                account_id=profile.account_id,
                first_name="Updated",
                display_name="Updated D.",
            )
        )

        assert profile.first_name == "Updated"
        assert profile.display_name == "Updated D."
        repo.update.assert_awaited_once()
        uow.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_update_profile_not_found(self) -> None:
        repo = _mock_repo()
        repo.get_by_account_id.return_value = None
        uow = _mock_uow()

        handler = UpdateProfileHandler(repo, uow)

        with pytest.raises(NotFoundException, match="Profile not found"):
            await handler.handle(UpdateProfileCommand(account_id=uuid.uuid4()))


# ---------------------------------------------------------------------------
# GetProfileHandler
# ---------------------------------------------------------------------------


class TestGetProfileHandler:
    @pytest.mark.asyncio
    async def test_get_profile_success(self) -> None:
        profile = _make_profile(first_name="Alice", last_name="W")
        repo = _mock_repo()
        repo.get_by_account_id.return_value = profile

        handler = GetProfileHandler(repo)
        result = await handler.handle(GetProfileQuery(account_id=profile.account_id))

        assert result.first_name == "Alice"
        assert result.last_name == "W"
        assert result.account_id == profile.account_id

    @pytest.mark.asyncio
    async def test_get_profile_not_found(self) -> None:
        repo = _mock_repo()
        repo.get_by_account_id.return_value = None

        handler = GetProfileHandler(repo)

        with pytest.raises(NotFoundException, match="Profile not found"):
            await handler.handle(GetProfileQuery(account_id=uuid.uuid4()))
