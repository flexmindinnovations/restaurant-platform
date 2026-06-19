"""promotions_module — Promotion and CouponUsage tables with RLS

Revision ID: 0009
Revises: 0008
Create Date: 2026-06-19 00:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0009'
down_revision: Union[str, None] = '0008'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS promotions")

    op.create_table(
        'promotions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('code', sa.String(50), nullable=False, unique=True),
        sa.Column('description', sa.String(500), nullable=False, server_default=''),
        sa.Column('promotion_type', sa.String(30), nullable=False),
        sa.Column('value', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('min_order_amount', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('min_order_currency', sa.String(3), nullable=True),
        sa.Column('max_discount_amount', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('max_discount_currency', sa.String(3), nullable=True),
        sa.Column('valid_from', sa.DateTime(timezone=True), nullable=False),
        sa.Column('valid_until', sa.DateTime(timezone=True), nullable=False),
        sa.Column('max_total_uses', sa.Integer(), nullable=True),
        sa.Column('max_uses_per_customer', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('total_uses', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('status', sa.String(20), nullable=False, server_default='ACTIVE'),
        sa.Column('restaurant_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        schema='promotions',
    )

    op.create_index('ix_promotions_code', 'promotions', ['code'], schema='promotions')
    op.create_index('ix_promotions_status', 'promotions', ['status'], schema='promotions')
    op.create_index('ix_promotions_restaurant_id', 'promotions', ['restaurant_id'], schema='promotions')

    op.create_table(
        'coupon_usages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('promotion_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('order_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('discount_amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('discount_currency', sa.String(3), nullable=False, server_default='USD'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        schema='promotions',
    )

    op.create_index('ix_coupon_usages_promotion_id', 'coupon_usages', ['promotion_id'], schema='promotions')
    op.create_index('ix_coupon_usages_customer_id', 'coupon_usages', ['customer_id'], schema='promotions')
    op.create_index('ix_coupon_usages_order_id', 'coupon_usages', ['order_id'], schema='promotions')

    op.execute("""
        ALTER TABLE promotions.promotions ENABLE ROW LEVEL SECURITY;
        CREATE POLICY promotions_tenant_isolation ON promotions.promotions
            USING (restaurant_id IS NULL OR restaurant_id = current_setting('app.current_restaurant_id')::uuid);

        ALTER TABLE promotions.coupon_usages ENABLE ROW LEVEL SECURITY;
        CREATE POLICY coupon_usages_tenant_isolation ON promotions.coupon_usages
            USING (true);
    """)


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS coupon_usages_tenant_isolation ON promotions.coupon_usages")
    op.execute("DROP POLICY IF EXISTS promotions_tenant_isolation ON promotions.promotions")
    op.drop_table('coupon_usages', schema='promotions')
    op.drop_table('promotions', schema='promotions')
    op.execute("DROP SCHEMA IF EXISTS promotions")
