import uuid

import jwt
import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings


@pytest.fixture(scope="module")
def setup_integration_services():
    from app.config import get_settings
    from app.main import _wire_event_handlers  # noqa: PLC2701
    from shared.infrastructure.database import init_engine
    from shared.infrastructure.redis import init_redis

    settings = get_settings()
    init_engine(settings.database_url)
    init_redis(settings.redis_url)
    _wire_event_handlers()


@pytest.mark.integration
async def test_full_business_and_auth_flow(client: AsyncClient, db_session: AsyncSession):
    email = f"owner_{uuid.uuid4().hex[:8]}@example.com"
    password = "SecurePassword123!"

    # 1. Register a new user with RESTAURANT_OWNER role
    register_response = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "phone_number": "+12345678901", "roles": ["RESTAURANT_OWNER"]},
    )

    assert register_response.status_code == 201
    resp_data = register_response.json()
    account_id = uuid.UUID(resp_data["data"]["id"])

    # 2. Verify account is in DB and profile is automatically created (via Event Bus)
    result = await db_session.execute(
        text("SELECT email, is_verified, verification_token FROM identity.accounts WHERE id = :id"),
        {"id": account_id},
    )
    account_row = result.one_or_none()
    assert account_row is not None
    assert account_row.email == email
    assert account_row.is_verified is False

    # Check Profile (cross-module — use raw SQL to avoid importing users models)
    profile_result = await db_session.execute(
        text("SELECT first_name FROM users.profiles WHERE account_id = :id"),
        {"id": account_id},
    )
    profile_row = profile_result.one_or_none()
    assert profile_row is not None
    assert profile_row.first_name == email.split("@", maxsplit=1)[0].capitalize()

    # 3. Verify email via endpoint
    verify_response = await client.post(
        "/api/v1/auth/verify-email",
        json={
            "email": email,
            "token": account_row.verification_token,
        },
    )
    assert verify_response.status_code == 200

    # Refresh DB session & verify status
    await db_session.commit()
    result = await db_session.execute(
        text("SELECT is_verified, verification_token FROM identity.accounts WHERE id = :id"),
        {"id": account_id},
    )
    account_row = result.one()
    assert account_row.is_verified is True
    assert account_row.verification_token is None

    # 4. Login to retrieve access/refresh tokens
    login_response = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert login_response.status_code == 200
    tokens = login_response.json()["data"]
    access_token = tokens["access_token"]

    # 5. Fetch profile using access token
    headers = {"Authorization": f"Bearer {access_token}"}
    profile_response = await client.get("/api/v1/me", headers=headers)
    assert profile_response.status_code == 200
    profile_data = profile_response.json()["data"]
    assert profile_data["account_id"] == str(account_id)

    # 6. Update Profile
    update_response = await client.patch(
        "/api/v1/me",
        headers=headers,
        json={
            "first_name": "UpdatedOwner",
            "last_name": "LastName",
            "display_name": "Business Owner",
            "avatar_url": "http://avatar.jpg",
            "preferred_language": "en",
        },
    )
    assert update_response.status_code == 200

    # Verify profile updated in DB (raw SQL to avoid cross-module import)
    await db_session.commit()
    profile_result = await db_session.execute(
        text("SELECT first_name, display_name FROM users.profiles WHERE account_id = :id"),
        {"id": account_id},
    )
    profile_row = profile_result.one()
    assert profile_row.first_name == "UpdatedOwner"
    assert profile_row.display_name == "Business Owner"

    # 7. Register a Restaurant (Owner Role allowed)
    restaurant_name = f"My Gourmet {uuid.uuid4().hex[:4]}"
    reg_rest_response = await client.post(
        "/api/v1/restaurants",
        headers=headers,
        json={
            "name": restaurant_name,
            "phone": "+12345678902",
            "email": "contact@gourmet.com",
            "address_street": "123 Main St",
            "address_city": "New York",
            "address_state": "NY",
            "address_postal_code": "10001",
            "address_country": "US",
            "address_latitude": 40.7128,
            "address_longitude": -74.0060,
            "cuisine_types": ["Italian", "French"],
            "description": "Gourmet dining",
            "operating_hours": {"monday": {"open": "09:00", "close": "22:00"}},
        },
    )
    assert reg_rest_response.status_code == 201
    rest_data = reg_rest_response.json()["data"]
    restaurant_id = uuid.UUID(rest_data["id"])
    assert rest_data["name"] == restaurant_name
    assert rest_data["owner_id"] == str(account_id)
    assert rest_data["is_verified"] is False

    # 8. Update Restaurant (Owner should have access)
    update_rest_response = await client.patch(
        f"/api/v1/restaurants/{restaurant_id}",
        headers=headers,
        json={
            "name": f"{restaurant_name} Updated",
            "phone": "+12345678902",
            "email": "contact@gourmet.com",
            "address_street": "123 Main St",
            "address_city": "New York",
            "address_state": "NY",
            "address_postal_code": "10001",
            "address_country": "US",
            "operating_hours": {"monday": {"open": "09:00", "close": "22:00"}},
        },
    )
    assert update_rest_response.status_code == 200

    # 9. Verify Restaurant using Super Admin
    settings = get_settings()
    admin_payload = {"sub": str(uuid.uuid4()), "roles": ["SUPER_ADMIN"], "type": "access", "exp": 9999999999}
    admin_token = jwt.encode(admin_payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    verify_rest_resp = await client.post(f"/api/v1/admin/restaurants/{restaurant_id}/verify", headers=admin_headers)
    assert verify_rest_resp.status_code == 200

    # Verify database state (raw SQL to avoid cross-module import)
    await db_session.commit()
    rest_result = await db_session.execute(
        text("SELECT is_verified FROM restaurants.restaurants WHERE id = :id"),
        {"id": restaurant_id},
    )
    rest_row = rest_result.one()
    assert rest_row.is_verified is True
