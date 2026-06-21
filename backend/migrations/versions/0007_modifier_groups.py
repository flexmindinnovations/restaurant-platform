"""modifier_groups — ModifierGroup and Modifier tables

Revision ID: 0007
Revises: 0006
Create Date: 2026-06-18 18:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0007'
down_revision: Union[str, None] = '0006'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'modifier_groups',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('menu_item_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('menus.menu_items.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('restaurant_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('selection_type', sa.String(20), server_default='SINGLE', nullable=False),
        sa.Column('min_selections', sa.Integer(), server_default='0', nullable=False),
        sa.Column('max_selections', sa.Integer(), server_default='1', nullable=False),
        sa.Column('is_required', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('display_order', sa.Integer(), server_default='0', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        schema='menus',
    )

    op.create_table(
        'modifiers',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('modifier_group_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('menus.modifier_groups.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('price_adjustment_amount', sa.Numeric(precision=10, scale=2), server_default='0', nullable=False),
        sa.Column('price_adjustment_currency', sa.String(3), server_default='USD', nullable=False),
        sa.Column('is_default', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('is_available', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('display_order', sa.Integer(), server_default='0', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        schema='menus',
    )

    # RLS policies
    op.execute("ALTER TABLE menus.modifier_groups ENABLE ROW LEVEL SECURITY")
    op.execute("""
        CREATE POLICY modifier_groups_tenant_isolation ON menus.modifier_groups
            USING (restaurant_id = current_setting('app.current_restaurant_id')::uuid)
    """)


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS modifier_groups_tenant_isolation ON menus.modifier_groups")
    op.drop_table('modifiers', schema='menus')
    op.drop_table('modifier_groups', schema='menus')
