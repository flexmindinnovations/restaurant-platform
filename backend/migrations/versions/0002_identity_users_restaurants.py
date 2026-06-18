"""identity_users_restaurants

Revision ID: 0002
Revises: 0001
Create Date: 2026-06-17 19:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0002'
down_revision: Union[str, None] = '0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 0. Define RLS helper function and procedure
    op.execute("""
    CREATE OR REPLACE FUNCTION get_current_restaurant_id() RETURNS text AS $$
    BEGIN
        RETURN current_setting('app.current_restaurant_id', true);
    END;
    $$ LANGUAGE plpgsql STABLE;
    """)

    op.execute("""
    CREATE OR REPLACE PROCEDURE enable_tenant_rls(
        table_schema text,
        table_name text,
        tenant_column text DEFAULT 'restaurant_id'
    ) AS $$
    BEGIN
        EXECUTE format('ALTER TABLE %I.%I ENABLE ROW LEVEL SECURITY', table_schema, table_name);
        EXECUTE format('ALTER TABLE %I.%I FORCE ROW LEVEL SECURITY', table_schema, table_name);
        EXECUTE format('DROP POLICY IF EXISTS tenant_isolation_policy ON %I.%I', table_schema, table_name);
        EXECUTE format(
            'CREATE POLICY tenant_isolation_policy ON %I.%I AS RESTRICTIVE USING (%I = get_current_restaurant_id()::uuid)',
            table_schema,
            table_name,
            tenant_column
        );
    END;
    $$ LANGUAGE plpgsql;
    """)

    # 1. Create identity.accounts table
    op.create_table(
        'accounts',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('phone_number', sa.String(length=50), nullable=True),
        sa.Column('is_verified', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('verification_token', sa.String(length=255), nullable=True),
        sa.Column('reset_token', sa.String(length=255), nullable=True),
        sa.Column('reset_token_expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('roles', postgresql.JSONB(astext_type=sa.Text()), server_default='[]', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        schema='identity'
    )
    op.create_index('ix_identity_accounts_email', 'accounts', ['email'], unique=True, schema='identity')
    op.create_index('ix_identity_accounts_phone_number', 'accounts', ['phone_number'], unique=False, schema='identity')

    # 2. Create identity.refresh_tokens table
    op.create_table(
        'refresh_tokens',
        sa.Column('token_hash', sa.String(length=255), nullable=False),
        sa.Column('account_id', sa.UUID(), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_revoked', sa.Boolean(), server_default='false', nullable=False),
        sa.ForeignKeyConstraint(['account_id'], ['identity.accounts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('token_hash'),
        schema='identity'
    )
    op.create_index('ix_identity_refresh_tokens_account_id', 'refresh_tokens', ['account_id'], unique=False, schema='identity')

    # 3. Create users.profiles table
    op.create_table(
        'profiles',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('account_id', sa.UUID(), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('display_name', sa.String(length=200), nullable=True),
        sa.Column('avatar_url', sa.String(length=255), nullable=True),
        sa.Column('preferred_language', sa.String(length=10), server_default='en', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('account_id'),
        schema='users'
    )
    op.create_index('ix_users_profiles_account_id', 'profiles', ['account_id'], unique=True, schema='users')

    # 4. Create restaurants.restaurants table
    op.create_table(
        'restaurants',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('owner_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('cuisine_types', postgresql.JSONB(astext_type=sa.Text()), server_default='[]', nullable=False),
        sa.Column('address_street', sa.String(length=255), nullable=False),
        sa.Column('address_city', sa.String(length=100), nullable=False),
        sa.Column('address_state', sa.String(length=100), nullable=False),
        sa.Column('address_postal_code', sa.String(length=20), nullable=False),
        sa.Column('address_country', sa.String(length=100), nullable=False),
        sa.Column('address_latitude', sa.Double(), nullable=True),
        sa.Column('address_longitude', sa.Double(), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('operating_hours', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('is_verified', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('rating_avg', sa.Numeric(precision=3, scale=2), server_default='0.00', nullable=False),
        sa.Column('total_reviews', sa.Integer(), server_default='0', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        schema='restaurants'
    )
    op.create_index('ix_restaurants_restaurants_owner_id', 'restaurants', ['owner_id'], unique=False, schema='restaurants')
    op.create_index('ix_restaurants_restaurants_name', 'restaurants', ['name'], unique=False, schema='restaurants')

    # 5. Enable Row-Level Security on restaurants table
    op.execute("CALL enable_tenant_rls('restaurants', 'restaurants', 'id')")


def downgrade() -> None:
    # 1. Disable RLS policies or drop tables
    op.execute("DROP POLICY IF EXISTS tenant_isolation_policy ON restaurants.restaurants")
    op.execute("ALTER TABLE restaurants.restaurants DISABLE ROW LEVEL SECURITY")

    # 2. Drop tables
    op.drop_table('restaurants', schema='restaurants')
    op.drop_table('profiles', schema='users')
    op.drop_table('refresh_tokens', schema='identity')
    op.drop_table('accounts', schema='identity')

    # 3. Drop helper procedure and function
    op.execute("DROP PROCEDURE IF EXISTS enable_tenant_rls(text, text, text)")
    op.execute("DROP FUNCTION IF EXISTS get_current_restaurant_id()")
