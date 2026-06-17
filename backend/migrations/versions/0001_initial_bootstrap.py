"""initial_bootstrap

Revision ID: 0001
Revises: 
Create Date: 2026-06-17 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Enable PostgreSQL extensions in public schema
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm SCHEMA public")
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis SCHEMA public")
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist SCHEMA public")

    # 2. Create the 11 module schemas
    schemas = [
        "identity",
        "users",
        "restaurants",
        "menus",
        "orders",
        "payments",
        "deliveries",
        "notifications",
        "reviews",
        "promotions",
        "analytics"
    ]
    for schema in schemas:
        op.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")

    # 3. Create Outbox Messages table in default (public) schema
    op.create_table(
        'outbox_messages',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('event_type', sa.String(length=255), nullable=False),
        sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('occurred_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    # 1. Drop outbox_messages table
    op.drop_table('outbox_messages')

    # 2. Drop the 11 module schemas
    schemas = [
        "identity",
        "users",
        "restaurants",
        "menus",
        "orders",
        "payments",
        "deliveries",
        "notifications",
        "reviews",
        "promotions",
        "analytics"
    ]
    for schema in schemas:
        op.execute(f"DROP SCHEMA IF EXISTS {schema} CASCADE")

    # 3. Drop PostgreSQL extensions
    op.execute("DROP EXTENSION IF EXISTS btree_gist CASCADE")
    op.execute("DROP EXTENSION IF EXISTS postgis CASCADE")
    op.execute("DROP EXTENSION IF EXISTS pg_trgm CASCADE")
