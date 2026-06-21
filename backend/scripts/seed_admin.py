"""
Seed script — creates a SUPER_ADMIN account if one doesn't already exist.

Uses the same database URL as the application (reads from backend/.env via config.py).

Usage (run from backend/ directory):
    uv run scripts/seed_admin.py

Optional env overrides:
    SEED_ADMIN_EMAIL=admin@example.com
    SEED_ADMIN_PASSWORD=MySecretPass!1
    SEED_ADMIN_PHONE=+1234567890
"""

import asyncio
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path

# Ensure the src directory is on the Python path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import bcrypt
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.config import get_settings

settings = get_settings()

import os

# ── Seed data ────────────────────────────────────────────────────
ADMIN_EMAIL = os.getenv("SEED_ADMIN_EMAIL", "admin@quickbite.com")
ADMIN_PASSWORD = os.getenv("SEED_ADMIN_PASSWORD", "Admin@123456")
ADMIN_PHONE = os.getenv("SEED_ADMIN_PHONE", "+1234567890")


# ── Helpers ──────────────────────────────────────────────────────
def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


async def seed(session: AsyncSession) -> None:
    # Check if a SUPER_ADMIN already exists
    result = await session.execute(
        text("""
            SELECT id, email
            FROM identity.accounts
            WHERE roles @> '["SUPER_ADMIN"]'::jsonb
            LIMIT 1
        """)
    )
    existing = result.fetchone()

    if existing:
        print(f"[OK]  SUPER_ADMIN already exists -> {existing.email}  (id: {existing.id})")
        print("      No changes made.")
        return

    # Check if the email is already taken (non-admin)
    dup = await session.execute(
        text("SELECT id FROM identity.accounts WHERE email = :email"),
        {"email": ADMIN_EMAIL},
    )
    if dup.fetchone():
        print(f"[WARN]  Email '{ADMIN_EMAIL}' is already registered (non-admin).")
        print("        Set SEED_ADMIN_EMAIL env var to a different address and re-run.")
        return

    account_id = uuid.uuid4()
    now = datetime.now(UTC)
    password_hash = hash_password(ADMIN_PASSWORD)

    import json

    await session.execute(
        text("""
            INSERT INTO identity.accounts
                (id, email, password_hash, phone_number, is_verified, is_active,
                 verification_token, roles, created_at, updated_at)
            VALUES
                (:id, :email, :password_hash, :phone, TRUE, TRUE,
                 NULL, CAST(:roles AS jsonb), :now, :now)
        """),
        {
            "id": str(account_id),
            "email": ADMIN_EMAIL,
            "password_hash": password_hash,
            "phone": ADMIN_PHONE,
            "roles": json.dumps(["SUPER_ADMIN"]),
            "now": now,
        },
    )
    await session.commit()

    print("[DONE]  SUPER_ADMIN created successfully!")
    print(f"    Email    : {ADMIN_EMAIL}")
    print(f"    Password : {ADMIN_PASSWORD}")
    print(f"    ID       : {account_id}")
    print()
    print("[WARN]  Change the password immediately after first login!")


# ── Entry point ──────────────────────────────────────────────────
async def main() -> None:
    db_url = settings.database_url
    # Mask password in output
    safe_url = db_url.replace(settings.db_password, "***")
    print(f"Connecting to -> {safe_url}")

    engine = create_async_engine(db_url, echo=False)
    Session = AsyncSession(engine)

    async with Session as session:
        await seed(session)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
