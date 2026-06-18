import uuid

import pytest

from modules.users.domain.entities.user_profile import UserProfile


@pytest.mark.unit
def test_user_profile_creation():
    account_id = uuid.uuid4()
    profile = UserProfile.create(
        account_id=account_id,
        first_name="John",
        last_name="Doe",
        preferred_language="fr",
    )

    assert profile.account_id == account_id
    assert profile.first_name == "John"
    assert profile.last_name == "Doe"
    assert profile.display_name == "John Doe"
    assert profile.preferred_language == "fr"
    assert profile.avatar_url is None


@pytest.mark.unit
def test_user_profile_update():
    account_id = uuid.uuid4()
    profile = UserProfile.create(
        account_id=account_id,
        first_name="John",
        last_name="Doe",
    )

    profile.update_profile(
        first_name="Jane",
        display_name="Jane D.",
        avatar_url="http://avatar.com/jane",
    )

    assert profile.first_name == "Jane"
    assert profile.last_name == "Doe"
    assert profile.display_name == "Jane D."
    assert profile.avatar_url == "http://avatar.com/jane"
