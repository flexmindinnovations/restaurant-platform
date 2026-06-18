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
    from app.main import _wire_event_handlers
    from shared.infrastructure.database import init_engine
    from shared.infrastructure.redis import init_redis

    settings = get_settings()
    init_engine(settings.database_url)
    init_redis(settings.redis_url)
    _wire_event_handlers()


@pytest.mark.integration
async def test_full_checkout_and_order_lifecycle(client: AsyncClient, db_session: AsyncSession):
    # Setup settings
    settings = get_settings()

    # 1. Register a Restaurant Owner
    owner_email = f"owner_{uuid.uuid4().hex[:8]}@example.com"
    password = "SecurePassword123!"

    owner_reg_resp = await client.post(
        "/api/v1/auth/register",
        json={"email": owner_email, "password": password, "phone_number": "+12345678901", "roles": ["RESTAURANT_OWNER"]},
    )
    assert owner_reg_resp.status_code == 201
    owner_id = uuid.UUID(owner_reg_resp.json()["data"]["id"])

    # Verify owner's email
    await db_session.commit()
    result = await db_session.execute(
        text("SELECT verification_token FROM identity.accounts WHERE id = :id"),
        {"id": owner_id},
    )
    token = result.scalar()
    verify_resp = await client.post(
        "/api/v1/auth/verify-email",
        json={"email": owner_email, "token": token},
    )
    assert verify_resp.status_code == 200

    # Login owner to get token
    owner_login_resp = await client.post("/api/v1/auth/login", json={"email": owner_email, "password": password})
    assert owner_login_resp.status_code == 200
    owner_access_token = owner_login_resp.json()["data"]["access_token"]
    owner_headers = {"Authorization": f"Bearer {owner_access_token}"}

    # 2. Register a Customer
    cust_email = f"customer_{uuid.uuid4().hex[:8]}@example.com"
    cust_reg_resp = await client.post(
        "/api/v1/auth/register",
        json={"email": cust_email, "password": password, "phone_number": "+12345678909", "roles": ["CUSTOMER"]},
    )
    assert cust_reg_resp.status_code == 201
    cust_id = uuid.UUID(cust_reg_resp.json()["data"]["id"])

    # Verify customer's email
    await db_session.commit()
    result = await db_session.execute(
        text("SELECT verification_token FROM identity.accounts WHERE id = :id"),
        {"id": cust_id},
    )
    token = result.scalar()
    verify_resp = await client.post(
        "/api/v1/auth/verify-email",
        json={"email": cust_email, "token": token},
    )
    assert verify_resp.status_code == 200

    # Login customer
    cust_login_resp = await client.post("/api/v1/auth/login", json={"email": cust_email, "password": password})
    assert cust_login_resp.status_code == 200
    cust_access_token = cust_login_resp.json()["data"]["access_token"]
    cust_headers = {"Authorization": f"Bearer {cust_access_token}"}

    # 3. Create a Restaurant (using owner token)
    restaurant_name = f"My Pasta Place {uuid.uuid4().hex[:4]}"
    reg_rest_resp = await client.post(
        "/api/v1/restaurants",
        headers=owner_headers,
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
            "cuisine_types": ["Italian"],
            "description": "Delicious pasta",
            "operating_hours": {"monday": {"open": "09:00", "close": "22:00"}},
        },
    )
    assert reg_rest_resp.status_code == 201
    restaurant_id = uuid.UUID(reg_rest_resp.json()["data"]["id"])

    # 4. Verify Restaurant (using Super Admin)
    admin_payload = {"sub": str(uuid.uuid4()), "roles": ["SUPER_ADMIN"], "type": "access", "exp": 9999999999}
    admin_token = jwt.encode(admin_payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    verify_rest_resp = await client.post(f"/api/v1/admin/restaurants/{restaurant_id}/verify", headers=admin_headers)
    assert verify_rest_resp.status_code == 200

    # 5. Create Owner JWT with restaurant_id claim (required by Menus context)
    owner_payload = {
        "sub": str(owner_id),
        "roles": ["RESTAURANT_OWNER"],
        "restaurant_id": str(restaurant_id),
        "type": "access",
        "exp": 9999999999
    }
    owner_token = jwt.encode(owner_payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    owner_headers = {"Authorization": f"Bearer {owner_token}"}

    # 6. Create Menu and Menu Item (using owner token)
    menu_resp = await client.post(
        "/api/v1/menus",
        headers=owner_headers,
        json={"name": "Gourmet Pasta", "description": "Authentic Italian Pasta"},
    )
    assert menu_resp.status_code == 201
    menu_id = uuid.UUID(menu_resp.json()["data"]["id"])

    item_resp = await client.post(
        f"/api/v1/menus/{menu_id}/items",
        headers=owner_headers,
        json={
            "name": "Fettuccine Alfredo",
            "description": "Rich creamy white sauce pasta",
            "price_amount": "16.50",
            "price_currency": "USD"
        }
    )
    assert item_resp.status_code == 201
    item_id = uuid.UUID(item_resp.json()["data"]["id"])

    # 7. Customer Cart Operations
    # Add item to cart
    add_cart_resp = await client.post(
        "/api/v1/checkout/cart/items",
        headers=cust_headers,
        json={"menu_item_id": str(item_id), "quantity": 1, "special_instructions": "Extra cheese"}
    )
    assert add_cart_resp.status_code == 201
    cart_data = add_cart_resp.json()["data"]
    assert cart_data["restaurant_id"] == str(restaurant_id)
    assert len(cart_data["items"]) == 1
    assert cart_data["items"][0]["menu_item_id"] == str(item_id)
    assert cart_data["items"][0]["quantity"] == 1

    # Get cart
    get_cart_resp = await client.get("/api/v1/checkout/cart", headers=cust_headers)
    assert get_cart_resp.status_code == 200
    assert len(get_cart_resp.json()["data"]["items"]) == 1

    # Update item quantity
    patch_cart_resp = await client.patch(
        f"/api/v1/checkout/cart/items/{item_id}",
        headers=cust_headers,
        json={"quantity": 2}
    )
    assert patch_cart_resp.status_code == 200
    assert patch_cart_resp.json()["data"]["items"][0]["quantity"] == 2

    # 8. Customer Places Order
    place_order_resp = await client.post(
        "/api/v1/checkout/place-order",
        headers=cust_headers,
        json={
            "delivery_address_street": "456 Customer Ave",
            "delivery_address_city": "Seattle",
            "delivery_address_state": "WA",
            "delivery_address_postal_code": "98101",
            "delivery_address_country": "US",
            "tip_amount": "3.50",
            "delivery_notes": "Call upon arrival"
        }
    )
    assert place_order_resp.status_code == 201
    order_id = uuid.UUID(place_order_resp.json()["data"]["order_id"])

    # Cart should be cleared after checkout
    get_cart_clear_resp = await client.get("/api/v1/checkout/cart", headers=cust_headers)
    assert get_cart_clear_resp.status_code == 200
    assert len(get_cart_clear_resp.json()["data"]["items"]) == 0

    # 9. View Order Details
    # Customer gets details
    get_order_resp = await client.get(f"/api/v1/orders/{order_id}", headers=cust_headers)
    assert get_order_resp.status_code == 200
    order_data = get_order_resp.json()["data"]
    assert order_data["status"] == "PENDING"
    assert order_data["restaurant_id"] == str(restaurant_id)
    assert order_data["customer_id"] == str(cust_id)
    assert order_data["subtotal_amount"] == "33.00"  # 16.50 * 2
    assert order_data["tip_amount"] == "3.50"

    # Owner gets details
    get_order_owner_resp = await client.get(f"/api/v1/orders/{order_id}", headers=owner_headers)
    assert get_order_owner_resp.status_code == 200

    # 10. Owner Confirms Order
    confirm_resp = await client.post(f"/api/v1/orders/{order_id}/confirm", headers=owner_headers)
    assert confirm_resp.status_code == 200

    # Check status
    get_order_confirmed_resp = await client.get(f"/api/v1/orders/{order_id}", headers=cust_headers)
    assert get_order_confirmed_resp.json()["data"]["status"] == "CONFIRMED"

    # 11. Owner updates status to PREPARING
    status_resp = await client.post(
        f"/api/v1/orders/{order_id}/status",
        headers=owner_headers,
        json={"status": "PREPARING"}
    )
    assert status_resp.status_code == 200

    # Customer tries to cancel PREPARING order - should fail
    cancel_fail_resp = await client.post(
        f"/api/v1/orders/{order_id}/cancel",
        headers=cust_headers,
        json={"reason": "Changed my mind"}
    )
    assert cancel_fail_resp.status_code == 400 or cancel_fail_resp.status_code == 422
    # In standard domain validation, it raises ValidationException, which maps to 400 Bad Request

    # 12. Customer places a second order and cancels it while PENDING
    # Add to cart
    await client.post(
        "/api/v1/checkout/cart/items",
        headers=cust_headers,
        json={"menu_item_id": str(item_id), "quantity": 1}
    )
    # Place order
    place_order_2_resp = await client.post(
        "/api/v1/checkout/place-order",
        headers=cust_headers,
        json={
            "delivery_address_street": "456 Customer Ave",
            "delivery_address_city": "Seattle",
            "delivery_address_state": "WA",
            "delivery_address_postal_code": "98101",
            "delivery_address_country": "US",
            "tip_amount": "1.00",
        }
    )
    order_id_2 = uuid.UUID(place_order_2_resp.json()["data"]["order_id"])

    # Cancel order
    cancel_success_resp = await client.post(
        f"/api/v1/orders/{order_id_2}/cancel",
        headers=cust_headers,
        json={"reason": "Decided to cook instead"}
    )
    assert cancel_success_resp.status_code == 200

    # Check order 2 status
    get_order_2_resp = await client.get(f"/api/v1/orders/{order_id_2}", headers=cust_headers)
    assert get_order_2_resp.json()["data"]["status"] == "CANCELLED"
    assert get_order_2_resp.json()["data"]["cancellation_reason"] == "Decided to cook instead"
