"""menus_module

Revision ID: 0003
Revises: 0002
Create Date: 2026-06-18 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0003'
down_revision: Union[str, None] = '0002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create menus.menus table
    op.create_table(
        'menus',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('restaurant_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        schema='menus'
    )
    op.create_index('ix_menus_menus_restaurant_id', 'menus', ['restaurant_id'], unique=False, schema='menus')

    # 2. Create menus.categories table
    op.create_table(
        'categories',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('menu_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('display_order', sa.Integer(), server_default='0', nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['menu_id'], ['menus.menus.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='menus'
    )
    op.create_index('ix_menus_categories_menu_id', 'categories', ['menu_id'], unique=False, schema='menus')

    # 3. Create menus.menu_items table
    op.create_table(
        'menu_items',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('menu_id', sa.UUID(), nullable=False),
        sa.Column('category_id', sa.UUID(), nullable=True),
        sa.Column('restaurant_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('price_amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('price_currency', sa.String(length=3), server_default='USD', nullable=False),
        sa.Column('image_url', sa.String(length=500), nullable=True),
        sa.Column('display_order', sa.Integer(), server_default='0', nullable=False),
        sa.Column('is_available', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('dietary_labels', postgresql.JSONB(astext_type=sa.Text()), server_default='[]', nullable=False),
        sa.Column('preparation_time_minutes', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['menu_id'], ['menus.menus.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['category_id'], ['menus.categories.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        schema='menus'
    )
    op.create_index('ix_menus_menu_items_menu_id', 'menu_items', ['menu_id'], unique=False, schema='menus')
    op.create_index('ix_menus_menu_items_category_id', 'menu_items', ['category_id'], unique=False, schema='menus')
    op.create_index('ix_menus_menu_items_restaurant_id', 'menu_items', ['restaurant_id'], unique=False, schema='menus')

    # 4. Enable RLS on menu_items (tenant-scoped by restaurant_id)
    op.execute("CALL enable_tenant_rls('menus', 'menu_items', 'restaurant_id')")


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_isolation_policy ON menus.menu_items")
    op.execute("ALTER TABLE menus.menu_items DISABLE ROW LEVEL SECURITY")

    op.drop_table('menu_items', schema='menus')
    op.drop_table('categories', schema='menus')
    op.drop_table('menus', schema='menus')
