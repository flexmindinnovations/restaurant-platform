# ruff: noqa: E501, S311, PLR0914, PLR2004, PLR6201, ERA001
"""
Seed script — populates the database with realistic Indian restaurant data.

Creates: accounts, profiles, restaurants, menus, menu items, orders,
payments, deliveries, delivery partners, reviews, and promotions.

Usage (run from backend/ directory):
    uv run scripts/seed_data.py

Idempotent: checks for existing data before inserting.
"""

import asyncio
import json
import random
import sys
import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import bcrypt
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.config import get_settings

settings = get_settings()
CURRENCY = settings.default_currency


def _hash(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def _now() -> datetime:
    return datetime.now(UTC)


def _days_ago(n: int) -> datetime:
    return _now() - timedelta(days=n)


def _uuid() -> str:
    return str(uuid.uuid4())


# ── Fixed IDs (deterministic so script can detect existing data) ────
ADMIN_ID = "a0000000-0000-0000-0000-000000000001"
OWNER1_ID = "b0000000-0000-0000-0000-000000000001"
OWNER2_ID = "b0000000-0000-0000-0000-000000000002"
OWNER3_ID = "b0000000-0000-0000-0000-000000000003"
CUST1_ID = "c0000000-0000-0000-0000-000000000001"
CUST2_ID = "c0000000-0000-0000-0000-000000000002"
CUST3_ID = "c0000000-0000-0000-0000-000000000003"
CUST4_ID = "c0000000-0000-0000-0000-000000000004"
DEL1_ID = "d0000000-0000-0000-0000-000000000001"
DEL2_ID = "d0000000-0000-0000-0000-000000000002"
DEL3_ID = "d0000000-0000-0000-0000-000000000003"

REST1_ID = "e0000000-0000-0000-0000-000000000001"
REST2_ID = "e0000000-0000-0000-0000-000000000002"
REST3_ID = "e0000000-0000-0000-0000-000000000003"

MENU1_ID = "f0000000-0000-0000-0000-000000000001"
MENU2_ID = "f0000000-0000-0000-0000-000000000002"
MENU3_ID = "f0000000-0000-0000-0000-000000000003"

DEFAULT_PASSWORD = "Test@12345"


# ── Accounts ────────────────────────────────────────────────────────
ACCOUNTS = [
    # Super Admin
    {
        "id": ADMIN_ID,
        "email": "admin@quickbite.in",
        "phone": "+919876500001",
        "roles": ["SUPER_ADMIN"],
    },
    # Restaurant Owners
    {
        "id": OWNER1_ID,
        "email": "rajesh.kumar@spicegarden.in",
        "phone": "+919876500002",
        "roles": ["RESTAURANT_OWNER"],
    },
    {
        "id": OWNER2_ID,
        "email": "priya.sharma@tandoorpalace.in",
        "phone": "+919876500003",
        "roles": ["RESTAURANT_OWNER"],
    },
    {
        "id": OWNER3_ID,
        "email": "amit.patel@mumbaibites.in",
        "phone": "+919876500004",
        "roles": ["RESTAURANT_OWNER"],
    },
    # Customers
    {
        "id": CUST1_ID,
        "email": "ananya.verma@gmail.com",
        "phone": "+919876500005",
        "roles": ["CUSTOMER"],
    },
    {
        "id": CUST2_ID,
        "email": "vikram.singh@gmail.com",
        "phone": "+919876500006",
        "roles": ["CUSTOMER"],
    },
    {
        "id": CUST3_ID,
        "email": "neha.gupta@gmail.com",
        "phone": "+919876500007",
        "roles": ["CUSTOMER"],
    },
    {
        "id": CUST4_ID,
        "email": "arjun.reddy@gmail.com",
        "phone": "+919876500008",
        "roles": ["CUSTOMER"],
    },
    # Delivery Partners
    {
        "id": DEL1_ID,
        "email": "ravi.tiwari@quickbite.in",
        "phone": "+919876500009",
        "roles": ["DELIVERY_PARTNER"],
    },
    {
        "id": DEL2_ID,
        "email": "suresh.kumar@quickbite.in",
        "phone": "+919876500010",
        "roles": ["DELIVERY_PARTNER"],
    },
    {
        "id": DEL3_ID,
        "email": "deepak.yadav@quickbite.in",
        "phone": "+919876500011",
        "roles": ["DELIVERY_PARTNER"],
    },
]

PROFILES = [
    {"account_id": ADMIN_ID, "first_name": "Admin", "last_name": "QuickBite", "display_name": "Platform Admin"},
    {"account_id": OWNER1_ID, "first_name": "Rajesh", "last_name": "Kumar", "display_name": "Rajesh Kumar"},
    {"account_id": OWNER2_ID, "first_name": "Priya", "last_name": "Sharma", "display_name": "Priya Sharma"},
    {"account_id": OWNER3_ID, "first_name": "Amit", "last_name": "Patel", "display_name": "Amit Patel"},
    {"account_id": CUST1_ID, "first_name": "Ananya", "last_name": "Verma", "display_name": "Ananya Verma"},
    {"account_id": CUST2_ID, "first_name": "Vikram", "last_name": "Singh", "display_name": "Vikram Singh"},
    {"account_id": CUST3_ID, "first_name": "Neha", "last_name": "Gupta", "display_name": "Neha Gupta"},
    {"account_id": CUST4_ID, "first_name": "Arjun", "last_name": "Reddy", "display_name": "Arjun Reddy"},
    {"account_id": DEL1_ID, "first_name": "Ravi", "last_name": "Tiwari", "display_name": "Ravi Tiwari"},
    {"account_id": DEL2_ID, "first_name": "Suresh", "last_name": "Kumar", "display_name": "Suresh Kumar"},
    {"account_id": DEL3_ID, "first_name": "Deepak", "last_name": "Yadav", "display_name": "Deepak Yadav"},
]


# ── Restaurants ─────────────────────────────────────────────────────
RESTAURANTS = [
    {
        "id": REST1_ID,
        "owner_id": OWNER1_ID,
        "name": "Spice Garden",
        "description": "Authentic North Indian and Mughlai cuisine in the heart of Delhi. Famous for our tandoori platters and rich gravies.",
        "cuisine_types": ["North Indian", "Mughlai", "Tandoori"],
        "phone": "+911123456789",
        "email": "contact@spicegarden.in",
        "address_street": "23, Janpath Road",
        "address_city": "New Delhi",
        "address_state": "Delhi",
        "address_postal_code": "110001",
        "address_country": "India",
        "address_latitude": 28.6315,
        "address_longitude": 77.2167,
        "operating_hours": {
            "monday": {"open": "11:00", "close": "23:00"},
            "tuesday": {"open": "11:00", "close": "23:00"},
            "wednesday": {"open": "11:00", "close": "23:00"},
            "thursday": {"open": "11:00", "close": "23:00"},
            "friday": {"open": "11:00", "close": "23:30"},
            "saturday": {"open": "10:00", "close": "23:30"},
            "sunday": {"open": "10:00", "close": "23:00"},
        },
        "rating_avg": 4.5,
        "total_reviews": 3,
    },
    {
        "id": REST2_ID,
        "owner_id": OWNER2_ID,
        "name": "Tandoor Palace",
        "description": "Premium tandoori and North Indian dining experience in Koramangala. Wood-fired clay oven specialties.",
        "cuisine_types": ["Tandoori", "North Indian", "Kebabs"],
        "phone": "+918041234567",
        "email": "hello@tandoorpalace.in",
        "address_street": "45, 80 Feet Road, Koramangala",
        "address_city": "Bengaluru",
        "address_state": "Karnataka",
        "address_postal_code": "560034",
        "address_country": "India",
        "address_latitude": 12.9352,
        "address_longitude": 77.6245,
        "operating_hours": {
            "monday": {"open": "11:30", "close": "22:30"},
            "tuesday": {"open": "11:30", "close": "22:30"},
            "wednesday": {"open": "11:30", "close": "22:30"},
            "thursday": {"open": "11:30", "close": "22:30"},
            "friday": {"open": "11:30", "close": "23:00"},
            "saturday": {"open": "11:00", "close": "23:00"},
            "sunday": {"open": "11:00", "close": "22:30"},
        },
        "rating_avg": 4.3,
        "total_reviews": 3,
    },
    {
        "id": REST3_ID,
        "owner_id": OWNER3_ID,
        "name": "Mumbai Bites",
        "description": "Iconic Mumbai street food — Vada Pav, Pav Bhaji, Bhel Puri and more. The taste of Bandra at your doorstep.",
        "cuisine_types": ["Street Food", "Maharashtrian", "Chinese"],
        "phone": "+912226789012",
        "email": "order@mumbaibites.in",
        "address_street": "12, Hill Road, Bandra West",
        "address_city": "Mumbai",
        "address_state": "Maharashtra",
        "address_postal_code": "400050",
        "address_country": "India",
        "address_latitude": 19.0544,
        "address_longitude": 72.8371,
        "operating_hours": {
            "monday": {"open": "08:00", "close": "22:00"},
            "tuesday": {"open": "08:00", "close": "22:00"},
            "wednesday": {"open": "08:00", "close": "22:00"},
            "thursday": {"open": "08:00", "close": "22:00"},
            "friday": {"open": "08:00", "close": "23:00"},
            "saturday": {"open": "09:00", "close": "23:00"},
            "sunday": {"open": "09:00", "close": "22:00"},
        },
        "rating_avg": 4.1,
        "total_reviews": 2,
    },
]


# ── Delivery Partners ──────────────────────────────────────────────
DELIVERY_PARTNERS = [
    {
        "id": _uuid(),
        "account_id": DEL1_ID,
        "name": "Ravi Tiwari",
        "phone": "+919876500009",
        "vehicle_type": "MOTORCYCLE",
        "is_online": True,
        "is_available": True,
        "rating_avg": 4.8,
        "total_deliveries": 342,
    },
    {
        "id": _uuid(),
        "account_id": DEL2_ID,
        "name": "Suresh Kumar",
        "phone": "+919876500010",
        "vehicle_type": "BICYCLE",
        "is_online": True,
        "is_available": True,
        "rating_avg": 4.6,
        "total_deliveries": 218,
    },
    {
        "id": _uuid(),
        "account_id": DEL3_ID,
        "name": "Deepak Yadav",
        "phone": "+919876500011",
        "vehicle_type": "MOTORCYCLE",
        "is_online": False,
        "is_available": True,
        "rating_avg": 4.9,
        "total_deliveries": 567,
    },
]


# ── Menu items per restaurant ──────────────────────────────────────
# (name, price, description, dietary_labels, prep_time_minutes)
MENU_ITEMS_R1 = [
    # Starters
    (
        "Paneer Tikka",
        280,
        "Marinated cottage cheese grilled in clay oven with bell peppers and onions",
        ["vegetarian"],
        18,
    ),
    (
        "Samosa (2 pcs)",
        120,
        "Crispy pastry filled with spiced potatoes and peas, served with mint chutney",
        ["vegetarian", "vegan"],
        12,
    ),
    ("Chicken 65", 320, "Spicy deep-fried chicken marinated with red chillies, curry leaves, and ginger", [], 15),
    ("Hara Bhara Kebab", 220, "Green patties made with spinach, peas, and potatoes", ["vegetarian", "vegan"], 14),
    # Main Course
    ("Butter Chicken", 380, "Tender chicken in a rich, creamy tomato-butter gravy — our signature dish", [], 25),
    ("Dal Makhani", 260, "Black lentils slow-cooked overnight with butter and cream", ["vegetarian"], 20),
    (
        "Hyderabadi Biryani",
        350,
        "Fragrant basmati rice layered with spiced chicken, saffron and caramelised onions",
        [],
        30,
    ),
    ("Palak Paneer", 280, "Fresh cottage cheese cubes in a vibrant spinach gravy", ["vegetarian"], 20),
    ("Chole Bhature", 220, "Spiced chickpea curry served with fluffy deep-fried bread", ["vegetarian"], 18),
    # Breads
    ("Butter Naan", 60, "Soft leavened bread brushed with butter from the tandoor", ["vegetarian"], 5),
    ("Garlic Naan", 70, "Naan loaded with fresh garlic and coriander", ["vegetarian"], 5),
    ("Tandoori Roti", 40, "Whole wheat flatbread baked in the tandoor", ["vegetarian", "vegan"], 5),
    # Desserts
    ("Gulab Jamun (2 pcs)", 120, "Deep-fried milk dumplings soaked in rose-scented sugar syrup", ["vegetarian"], 8),
    ("Rasmalai", 150, "Soft paneer discs immersed in chilled, saffron-flavoured milk", ["vegetarian"], 8),
]

MENU_ITEMS_R2 = [
    ("Tandoori Chicken (Half)", 380, "Half chicken marinated in yogurt and spices, charred in tandoor", [], 22),
    ("Fish Tikka", 420, "Boneless fish fillets marinated with ajwain and grilled to perfection", [], 18),
    ("Seekh Kebab", 340, "Minced lamb on skewers with aromatic spices, grilled over charcoal", [], 20),
    ("Paneer Malai Tikka", 290, "Creamy marinated paneer cubes, mild and delicate", ["vegetarian"], 16),
    ("Rogan Josh", 440, "Kashmiri slow-cooked lamb curry with aromatic spices", [], 30),
    ("Kadai Paneer", 300, "Paneer tossed with bell peppers in a kadai masala", ["vegetarian"], 18),
    ("Chicken Biryani", 320, "Layered rice with tender chicken pieces, raita on the side", [], 28),
    ("Veg Biryani", 250, "Fragrant rice with mixed vegetables, saffron, and whole spices", ["vegetarian"], 25),
    ("Mutton Biryani", 450, "Rich and aromatic rice layered with succulent mutton pieces", [], 35),
    ("Dal Tadka", 200, "Yellow lentils tempered with cumin, garlic, and ghee", ["vegetarian"], 15),
    ("Laccha Paratha", 60, "Flaky, layered whole wheat paratha from the tandoor", ["vegetarian"], 6),
    ("Kulfi (Malai)", 100, "Traditional Indian frozen dessert — dense and creamy", ["vegetarian"], 5),
    ("Kheer", 130, "Slow-simmered rice pudding with cardamom, almonds, and pistachios", ["vegetarian"], 5),
]

MENU_ITEMS_R3 = [
    ("Vada Pav", 50, "Mumbai's iconic spiced potato fritter in a soft bun with chutneys", ["vegetarian", "vegan"], 8),
    ("Pav Bhaji", 150, "Spiced mashed vegetable curry served with buttered pav", ["vegetarian"], 15),
    ("Bhel Puri", 80, "Puffed rice tossed with onions, tomatoes, chutneys, and sev", ["vegetarian", "vegan"], 8),
    ("Sev Puri", 90, "Crispy puris topped with potato, chutneys, onion, and sev", ["vegetarian", "vegan"], 8),
    ("Misal Pav", 160, "Spicy sprouted moth beans curry with pav — Maharashtrian classic", ["vegetarian", "vegan"], 15),
    ("Thali — Veg", 250, "Complete meal: dal, sabzi, roti, rice, raita, papad, pickle, sweet", ["vegetarian"], 20),
    ("Thali — Non-Veg", 350, "Complete meal: chicken curry, dal, roti, rice, raita, papad, sweet", [], 22),
    ("Hakka Noodles", 180, "Stir-fried noodles with vegetables in Indo-Chinese style", ["vegetarian"], 12),
    ("Veg Manchurian", 200, "Crispy vegetable balls in a tangy Manchurian sauce", ["vegetarian"], 15),
    ("Masala Chai", 40, "Traditional Indian spiced tea with ginger and cardamom", ["vegetarian"], 5),
    ("Mango Lassi", 80, "Chilled yogurt drink blended with Alphonso mango pulp", ["vegetarian"], 5),
    ("Fresh Lime Soda", 60, "Freshly squeezed lime with soda — sweet or salted", ["vegetarian", "vegan"], 3),
]


# ── Promotions ─────────────────────────────────────────────────────
PROMOTIONS = [
    {
        "code": "WELCOME50",
        "description": "50% off on your first order! Maximum discount ₹150.",
        "promotion_type": "PERCENTAGE",
        "value": 50,
        "min_order_amount": 200,
        "min_order_currency": CURRENCY,
        "max_discount_amount": 150,
        "max_discount_currency": CURRENCY,
        "max_total_uses": 1000,
        "max_uses_per_customer": 1,
    },
    {
        "code": "FREEDEL",
        "description": "Free delivery on orders above ₹299.",
        "promotion_type": "FREE_DELIVERY",
        "value": 100,
        "min_order_amount": 299,
        "min_order_currency": CURRENCY,
        "max_discount_amount": None,
        "max_discount_currency": None,
        "max_total_uses": None,
        "max_uses_per_customer": 5,
    },
    {
        "code": "FESTIVE20",
        "description": "Festive season offer — 20% off up to ₹200.",
        "promotion_type": "PERCENTAGE",
        "value": 20,
        "min_order_amount": 500,
        "min_order_currency": CURRENCY,
        "max_discount_amount": 200,
        "max_discount_currency": CURRENCY,
        "max_total_uses": 500,
        "max_uses_per_customer": 3,
    },
    {
        "code": "FLAT100",
        "description": "Flat ₹100 off on orders above ₹399.",
        "promotion_type": "FIXED_AMOUNT",
        "value": 100,
        "min_order_amount": 399,
        "min_order_currency": CURRENCY,
        "max_discount_amount": 100,
        "max_discount_currency": CURRENCY,
        "max_total_uses": 2000,
        "max_uses_per_customer": 2,
        "restaurant_id": REST1_ID,
    },
]


async def _has_seed_data(session: AsyncSession) -> bool:
    result = await session.execute(
        text("SELECT id FROM identity.accounts WHERE id = :id"),
        {"id": OWNER1_ID},
    )
    return result.fetchone() is not None


async def _insert_accounts(session: AsyncSession) -> None:
    print("  [+] Creating accounts...")
    now = _now()
    pw = _hash(DEFAULT_PASSWORD)
    for acc in ACCOUNTS:
        await session.execute(
            text("""
                INSERT INTO identity.accounts
                    (id, email, password_hash, phone_number, is_verified, is_active,
                     verification_token, roles, created_at, updated_at)
                VALUES
                    (:id, :email, :pw, :phone, TRUE, TRUE,
                     NULL, CAST(:roles AS jsonb), :now, :now)
                ON CONFLICT (id) DO NOTHING
            """),
            {
                "id": acc["id"],
                "email": acc["email"],
                "pw": pw,
                "phone": acc["phone"],
                "roles": json.dumps(acc["roles"]),
                "now": now,
            },
        )


async def _insert_profiles(session: AsyncSession) -> None:
    print("  [+] Creating user profiles...")
    now = _now()
    for p in PROFILES:
        pid = _uuid()
        await session.execute(
            text("""
                INSERT INTO users.profiles
                    (id, account_id, first_name, last_name, display_name,
                     avatar_url, preferred_language, created_at, updated_at)
                VALUES
                    (:id, :account_id, :first, :last, :display,
                     NULL, 'en', :now, :now)
                ON CONFLICT (account_id) DO NOTHING
            """),
            {
                "id": pid,
                "account_id": p["account_id"],
                "first": p["first_name"],
                "last": p["last_name"],
                "display": p["display_name"],
                "now": now,
            },
        )


async def _insert_restaurants(session: AsyncSession) -> None:
    print("  [+] Creating restaurants...")
    now = _now()
    for r in RESTAURANTS:
        await session.execute(
            text("""
                INSERT INTO restaurants.restaurants
                    (id, owner_id, name, description, cuisine_types, phone, email,
                     address_street, address_city, address_state, address_postal_code,
                     address_country, address_latitude, address_longitude,
                     operating_hours, is_active, is_verified,
                     rating_avg, total_reviews, created_at, updated_at)
                VALUES
                    (:id, :owner_id, :name, :description, CAST(:cuisine AS jsonb), :phone, :email,
                     :street, :city, :state, :postal, :country, :lat, :lng,
                     CAST(:hours AS jsonb), TRUE, TRUE,
                     :rating_avg, :total_reviews, :now, :now)
                ON CONFLICT (id) DO NOTHING
            """),
            {
                "id": r["id"],
                "owner_id": r["owner_id"],
                "name": r["name"],
                "description": r["description"],
                "cuisine": json.dumps(r["cuisine_types"]),
                "phone": r["phone"],
                "email": r["email"],
                "street": r["address_street"],
                "city": r["address_city"],
                "state": r["address_state"],
                "postal": r["address_postal_code"],
                "country": r["address_country"],
                "lat": r["address_latitude"],
                "lng": r["address_longitude"],
                "hours": json.dumps(r["operating_hours"]),
                "rating_avg": r["rating_avg"],
                "total_reviews": r["total_reviews"],
                "now": now,
            },
        )


async def _insert_delivery_partners(session: AsyncSession) -> None:
    print("  [+] Creating delivery partners...")
    now = _now()
    for dp in DELIVERY_PARTNERS:
        await session.execute(
            text("""
                INSERT INTO deliveries.delivery_partners
                    (id, account_id, name, phone, vehicle_type,
                     is_online, is_available, rating_avg, total_deliveries,
                     created_at, updated_at)
                VALUES
                    (:id, :account_id, :name, :phone, :vehicle,
                     :online, :available, :rating, :deliveries,
                     :now, :now)
                ON CONFLICT (id) DO NOTHING
            """),
            {
                "id": dp["id"],
                "account_id": dp["account_id"],
                "name": dp["name"],
                "phone": dp["phone"],
                "vehicle": dp["vehicle_type"],
                "online": dp["is_online"],
                "available": dp["is_available"],
                "rating": dp["rating_avg"],
                "deliveries": dp["total_deliveries"],
                "now": now,
            },
        )


async def _insert_menus(session: AsyncSession) -> dict[str, list[dict]]:
    """Insert menus and menu items. Returns {restaurant_id: [{item_id, name, price}, ...]}."""
    print("  [+] Creating menus and menu items...")
    now = _now()
    all_items: dict[str, list[dict]] = {}

    menu_data = [
        (REST1_ID, MENU1_ID, "Spice Garden — Full Menu", MENU_ITEMS_R1),
        (REST2_ID, MENU2_ID, "Tandoor Palace — Full Menu", MENU_ITEMS_R2),
        (REST3_ID, MENU3_ID, "Mumbai Bites — Full Menu", MENU_ITEMS_R3),
    ]

    for rest_id, menu_id, menu_name, items_list in menu_data:
        await session.execute(
            text("""
                INSERT INTO menus.menus (id, restaurant_id, name, description, is_active, created_at, updated_at)
                VALUES (:id, :rest_id, :name, NULL, TRUE, :now, :now)
                ON CONFLICT (id) DO NOTHING
            """),
            {"id": menu_id, "rest_id": rest_id, "name": menu_name, "now": now},
        )

        restaurant_items = []
        for name, price, desc, labels, prep_time in items_list:
            item_id = _uuid()
            await session.execute(
                text("""
                    INSERT INTO menus.menu_items
                        (id, menu_id, category_id, restaurant_id, name, description,
                         price_amount, price_currency, image_url, display_order,
                         is_available, dietary_labels, preparation_time_minutes,
                         created_at, updated_at)
                    VALUES
                        (:id, :menu_id, NULL, :rest_id, :name, :desc,
                         :price, :currency, NULL, 0,
                         TRUE, CAST(:labels AS jsonb), :prep,
                         :now, :now)
                """),
                {
                    "id": item_id,
                    "menu_id": menu_id,
                    "rest_id": rest_id,
                    "name": name,
                    "desc": desc,
                    "price": price,
                    "currency": CURRENCY,
                    "labels": json.dumps(labels),
                    "prep": prep_time,
                    "now": now,
                },
            )
            restaurant_items.append({"id": item_id, "name": name, "price": price})

        all_items[rest_id] = restaurant_items

    return all_items


async def _insert_orders(session: AsyncSession, all_items: dict[str, list[dict]]) -> list[dict]:
    """Insert realistic orders over the past 30 days. Returns list of order dicts."""
    print("  [+] Creating orders...")
    orders = []
    order_counter = 1000

    customers = [CUST1_ID, CUST2_ID, CUST3_ID, CUST4_ID]
    addresses = [
        ("14 MG Road", "New Delhi", "Delhi", "110001", "India"),
        ("78 Brigade Road", "Bengaluru", "Karnataka", "560025", "India"),
        ("32 Linking Road", "Mumbai", "Maharashtra", "400050", "India"),
        ("5 Park Street", "Kolkata", "West Bengal", "700016", "India"),
    ]

    for rest_id, items in all_items.items():
        for day_offset in range(28, 0, -1):
            orders_per_day = random.randint(1, 3)
            for _ in range(orders_per_day):
                order_counter += 1
                customer = random.choice(customers)
                addr = random.choice(addresses)
                placed_at = _days_ago(day_offset) + timedelta(
                    hours=random.randint(10, 21), minutes=random.randint(0, 59)
                )

                # Pick 1-4 random items
                selected = random.sample(items, k=min(random.randint(1, 4), len(items)))
                order_items = []
                subtotal = Decimal("0")
                for item in selected:
                    qty = random.randint(1, 3)
                    item_total = Decimal(str(item["price"])) * qty
                    subtotal += item_total
                    order_items.append({
                        "id": _uuid(),
                        "menu_item_id": item["id"],
                        "name": item["name"],
                        "price": item["price"],
                        "quantity": qty,
                    })

                tax = (subtotal * Decimal("0.05")).quantize(Decimal("0.01"))
                delivery_fee = Decimal("49")
                tip = Decimal(str(random.choice([0, 0, 20, 30, 50])))
                total = subtotal + tax + delivery_fee + tip

                status = random.choices(
                    ["COMPLETED", "DELIVERED", "CONFIRMED", "PREPARING", "CANCELLED"],
                    weights=[50, 20, 10, 10, 10],
                )[0]

                confirmed_at = placed_at + timedelta(minutes=random.randint(1, 5)) if status != "CANCELLED" else None
                preparing_at = (
                    confirmed_at + timedelta(minutes=random.randint(1, 3))
                    if status not in ("CANCELLED", "CONFIRMED")
                    else None
                )
                ready_at = (
                    preparing_at + timedelta(minutes=random.randint(15, 30))
                    if status in ("COMPLETED", "DELIVERED")
                    else None
                )
                delivered_at = (
                    ready_at + timedelta(minutes=random.randint(15, 40))
                    if status in ("COMPLETED", "DELIVERED")
                    else None
                )
                cancelled_at = placed_at + timedelta(minutes=random.randint(2, 10)) if status == "CANCELLED" else None

                order_id = _uuid()
                order_number = f"ORD-{order_counter}"

                orders.append({
                    "id": order_id,
                    "restaurant_id": rest_id,
                    "customer_id": customer,
                    "order_number": order_number,
                    "status": status,
                    "items": order_items,
                    "subtotal": subtotal,
                    "tax": tax,
                    "delivery_fee": delivery_fee,
                    "tip": tip,
                    "total": total,
                    "placed_at": placed_at,
                    "confirmed_at": confirmed_at,
                    "preparing_at": preparing_at,
                    "ready_at": ready_at,
                    "delivered_at": delivered_at,
                    "cancelled_at": cancelled_at,
                    "address": addr,
                })

                now_ts = _now()
                await session.execute(
                    text("""
                        INSERT INTO orders.orders
                            (id, restaurant_id, customer_id, order_number, status,
                             delivery_address_street, delivery_address_city,
                             delivery_address_state, delivery_address_postal_code,
                             delivery_address_country, delivery_notes,
                             subtotal_amount, subtotal_currency,
                             tax_amount, tax_currency,
                             delivery_fee_amount, delivery_fee_currency,
                             tip_amount, tip_currency,
                             total_amount, total_currency,
                             cancellation_reason,
                             placed_at, confirmed_at, preparing_at, ready_at,
                             picked_up_at, delivered_at, cancelled_at,
                             created_at, updated_at)
                        VALUES
                            (:id, :rest_id, :cust_id, :order_num, :status,
                             :street, :city, :state, :postal, :country, NULL,
                             :subtotal, :cur, :tax, :cur, :del_fee, :cur, :tip, :cur, :total, :cur,
                             :cancel_reason,
                             :placed, :confirmed, :preparing, :ready,
                             :ready, :delivered, :cancelled,
                             :now, :now)
                    """),
                    {
                        "id": order_id,
                        "rest_id": rest_id,
                        "cust_id": customer,
                        "order_num": order_number,
                        "status": status,
                        "street": addr[0],
                        "city": addr[1],
                        "state": addr[2],
                        "postal": addr[3],
                        "country": addr[4],
                        "subtotal": str(subtotal),
                        "tax": str(tax),
                        "del_fee": str(delivery_fee),
                        "tip": str(tip),
                        "total": str(total),
                        "cur": CURRENCY,
                        "cancel_reason": "Changed my mind" if status == "CANCELLED" else None,
                        "placed": placed_at,
                        "confirmed": confirmed_at,
                        "preparing": preparing_at,
                        "ready": ready_at,
                        "delivered": delivered_at,
                        "cancelled": cancelled_at,
                        "now": now_ts,
                    },
                )

                for oi in order_items:
                    await session.execute(
                        text("""
                            INSERT INTO orders.order_items
                                (id, order_id, menu_item_id, name,
                                 price_amount, price_currency, quantity,
                                 special_instructions, created_at, updated_at)
                            VALUES
                                (:id, :order_id, :menu_item_id, :name,
                                 :price, :cur, :qty, NULL, :now, :now)
                        """),
                        {
                            "id": oi["id"],
                            "order_id": order_id,
                            "menu_item_id": oi["menu_item_id"],
                            "name": oi["name"],
                            "price": oi["price"],
                            "cur": CURRENCY,
                            "qty": oi["quantity"],
                            "now": now_ts,
                        },
                    )

    return orders


async def _insert_payments(session: AsyncSession, orders: list[dict]) -> None:
    print("  [+] Creating payments...")
    now = _now()
    for o in orders:
        status_map = {
            "COMPLETED": "CAPTURED",
            "DELIVERED": "CAPTURED",
            "CONFIRMED": "AUTHORIZED",
            "PREPARING": "AUTHORIZED",
            "CANCELLED": "VOIDED",
        }
        pay_status = status_map.get(o["status"], "PENDING")
        captured_at = o["delivered_at"] if pay_status == "CAPTURED" else None

        await session.execute(
            text("""
                INSERT INTO payments.payments
                    (id, order_id, customer_id, restaurant_id,
                     amount_cents, currency, status,
                     payment_method_type, payment_method_id,
                     gateway_transaction_id, gateway_response,
                     failure_reason, captured_at, refunded_at,
                     created_at, updated_at)
                VALUES
                    (:id, :order_id, :cust_id, :rest_id,
                     :cents, :cur, :status,
                     'UPI', NULL,
                     :gateway_txn, NULL,
                     NULL, :captured, NULL,
                     :now, :now)
            """),
            {
                "id": _uuid(),
                "order_id": o["id"],
                "cust_id": o["customer_id"],
                "rest_id": o["restaurant_id"],
                "cents": int(o["total"] * 100),
                "cur": CURRENCY,
                "status": pay_status,
                "gateway_txn": f"upi_{uuid.uuid4().hex[:16]}",
                "captured": captured_at,
                "now": now,
            },
        )


async def _insert_deliveries(session: AsyncSession, orders: list[dict]) -> None:
    print("  [+] Creating deliveries...")
    now = _now()
    partner_ids = [dp["id"] for dp in DELIVERY_PARTNERS]

    for o in orders:
        if o["status"] == "CANCELLED":
            continue

        del_status_map = {
            "COMPLETED": "DELIVERED",
            "DELIVERED": "DELIVERED",
            "CONFIRMED": "ASSIGNED",
            "PREPARING": "PARTNER_EN_ROUTE_TO_PICKUP",
        }
        del_status = del_status_map.get(o["status"], "PENDING_ASSIGNMENT")

        partner_id = random.choice(partner_ids) if del_status != "PENDING_ASSIGNMENT" else None
        est_pickup = (o["confirmed_at"] or o["placed_at"]) + timedelta(minutes=20)
        act_pickup = o["ready_at"]
        est_delivery = est_pickup + timedelta(minutes=30)
        act_delivery = o["delivered_at"]

        await session.execute(
            text("""
                INSERT INTO deliveries.deliveries
                    (id, order_id, restaurant_id, partner_id,
                     pickup_address, delivery_address, status,
                     estimated_pickup_time, actual_pickup_time,
                     estimated_delivery_time, actual_delivery_time,
                     distance_km, proof_of_delivery_url,
                     created_at, updated_at)
                VALUES
                    (:id, :order_id, :rest_id, :partner_id,
                     :pickup_addr, :del_addr, :status,
                     :est_pickup, :act_pickup,
                     :est_delivery, :act_delivery,
                     :distance, NULL,
                     :now, :now)
            """),
            {
                "id": _uuid(),
                "order_id": o["id"],
                "rest_id": o["restaurant_id"],
                "partner_id": partner_id,
                "pickup_addr": f"Restaurant pickup — {o['address'][1]}",
                "del_addr": f"{o['address'][0]}, {o['address'][1]}",
                "status": del_status,
                "est_pickup": est_pickup,
                "act_pickup": act_pickup,
                "est_delivery": est_delivery,
                "act_delivery": act_delivery,
                "distance": round(random.uniform(1.5, 8.0), 1),
                "now": now,
            },
        )


async def _insert_reviews(session: AsyncSession, orders: list[dict]) -> None:
    print("  [+] Creating reviews...")
    now = _now()

    completed_orders = [o for o in orders if o["status"] in ("COMPLETED", "DELIVERED")]
    review_candidates = random.sample(completed_orders, k=min(12, len(completed_orders)))

    comments = [
        (5, "Absolutely fantastic! The Butter Chicken was divine and naan was fresh. Will order again.", "POSITIVE"),
        (5, "Best biryani in the city, no exaggeration. Perfectly spiced and generous portions.", "POSITIVE"),
        (4, "Great food, delivery was a bit late but the taste made up for it. Recommended!", "POSITIVE"),
        (4, "Tasty and well-packed. Portions could be slightly larger for the price though.", "POSITIVE"),
        (4, "The Paneer Tikka was excellent. Fresh ingredients, you can taste the quality.", "POSITIVE"),
        (3, "Food was decent but arrived lukewarm. Taste was good once reheated.", "NEUTRAL"),
        (3, "Average experience. The naan was good but the gravy was too oily for my taste.", "NEUTRAL"),
        (4, "Vada Pav was spot on — crispy and spicy just like Mumbai streets. Love it!", "POSITIVE"),
        (5, "Pav Bhaji was heavenly. Generous butter, perfect spice level. My comfort food.", "POSITIVE"),
        (2, "Order was missing one item and the delivery took over an hour. Disappointing.", "NEGATIVE"),
        (4, "Consistent quality every time I order. The Thali is a complete meal and great value.", "POSITIVE"),
        (5, "Outstanding Rogan Josh! Tender meat, rich gravy. Restaurant quality at home.", "POSITIVE"),
    ]

    used_orders = set()
    for o in review_candidates:
        if o["id"] in used_orders:
            continue
        used_orders.add(o["id"])

        rating, comment, sentiment = random.choice(comments)
        await session.execute(
            text("""
                INSERT INTO reviews.reviews
                    (id, order_id, customer_id, restaurant_id,
                     rating, comment, sentiment,
                     is_flagged, flag_reason, reply, replied_at,
                     images, created_at, updated_at)
                VALUES
                    (:id, :order_id, :cust_id, :rest_id,
                     :rating, :comment, :sentiment,
                     FALSE, NULL, :reply, :replied_at,
                     CAST(:images AS varchar[]), :created, :now)
                ON CONFLICT (order_id) DO NOTHING
            """),
            {
                "id": _uuid(),
                "order_id": o["id"],
                "cust_id": o["customer_id"],
                "rest_id": o["restaurant_id"],
                "rating": rating,
                "comment": comment,
                "sentiment": sentiment,
                "reply": "Thank you for your feedback! We strive to serve the best." if rating >= 4 else None,
                "replied_at": now if rating >= 4 else None,
                "images": "{}",
                "created": o["delivered_at"] or now,
                "now": now,
            },
        )


async def _insert_promotions(session: AsyncSession) -> None:
    print("  [+] Creating promotions...")
    now = _now()
    valid_from = _days_ago(30)
    valid_until = now + timedelta(days=60)

    for promo in PROMOTIONS:
        await session.execute(
            text("""
                INSERT INTO promotions.promotions
                    (id, code, description, promotion_type, value,
                     min_order_amount, min_order_currency,
                     max_discount_amount, max_discount_currency,
                     valid_from, valid_until,
                     max_total_uses, max_uses_per_customer,
                     total_uses, status, restaurant_id,
                     created_at, updated_at)
                VALUES
                    (:id, :code, :desc, :type, :value,
                     :min_amt, :min_cur,
                     :max_amt, :max_cur,
                     :valid_from, :valid_until,
                     :max_uses, :max_per_cust,
                     0, 'ACTIVE', :rest_id,
                     :now, :now)
                ON CONFLICT (code) DO NOTHING
            """),
            {
                "id": _uuid(),
                "code": promo["code"],
                "desc": promo["description"],
                "type": promo["promotion_type"],
                "value": promo["value"],
                "min_amt": promo["min_order_amount"],
                "min_cur": promo.get("min_order_currency"),
                "max_amt": promo["max_discount_amount"],
                "max_cur": promo.get("max_discount_currency"),
                "valid_from": valid_from,
                "valid_until": valid_until,
                "max_uses": promo["max_total_uses"],
                "max_per_cust": promo["max_uses_per_customer"],
                "rest_id": promo.get("restaurant_id"),
                "now": now,
            },
        )


async def seed(session: AsyncSession) -> None:
    if await _has_seed_data(session):
        print("[OK]  Seed data already exists. Skipping.")
        print("      To re-seed, delete existing data first.")
        return

    await _insert_accounts(session)
    await _insert_profiles(session)
    await _insert_restaurants(session)
    await _insert_delivery_partners(session)
    all_items = await _insert_menus(session)
    orders = await _insert_orders(session, all_items)
    await _insert_payments(session, orders)
    await _insert_deliveries(session, orders)
    await _insert_reviews(session, orders)
    await _insert_promotions(session)

    await session.commit()

    print()
    print("[DONE]  Seed data inserted successfully!")
    print()
    print("  Accounts created:")
    for acc in ACCOUNTS:
        print(f"    {acc['roles'][0]:<20} {acc['email']:<40} (password: {DEFAULT_PASSWORD})")
    print()
    print(f"  Restaurants:       {len(RESTAURANTS)}")
    print(f"  Menu items:        {sum(len(v) for v in all_items.values())}")
    print(f"  Orders:            {len(orders)}")
    print(f"  Delivery partners: {len(DELIVERY_PARTNERS)}")
    print(f"  Promotions:        {len(PROMOTIONS)}")
    print(f"  Currency:          {CURRENCY}")


async def main() -> None:
    db_url = settings.database_url
    safe_url = db_url.replace(settings.db_password, "***")
    print(f"Connecting to -> {safe_url}")

    engine = create_async_engine(db_url, echo=False)
    async with AsyncSession(engine) as session:
        await seed(session)
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
