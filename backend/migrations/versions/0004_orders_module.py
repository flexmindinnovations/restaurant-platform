"""orders_module

Revision ID: 0004
Revises: 0003
Create Date: 2026-06-18 12:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0004'
down_revision: Union[str, None] = '0003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create orders.carts table
    op.create_table(
        'carts',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('restaurant_id', sa.UUID(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        schema='orders'
    )

    # 2. Create orders.cart_items table
    op.create_table(
        'cart_items',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('cart_id', sa.UUID(), nullable=False),
        sa.Column('menu_item_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('price_amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('price_currency', sa.String(length=3), server_default='USD', nullable=False),
        sa.Column('quantity', sa.Integer(), server_default='1', nullable=False),
        sa.Column('special_instructions', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['cart_id'], ['orders.carts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='orders'
    )
    op.create_index('ix_orders_cart_items_cart_id', 'cart_items', ['cart_id'], unique=False, schema='orders')

    # 3. Create orders.orders table
    op.create_table(
        'orders',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('restaurant_id', sa.UUID(), nullable=False),
        sa.Column('customer_id', sa.UUID(), nullable=False),
        sa.Column('order_number', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('delivery_address_street', sa.String(length=255), nullable=False),
        sa.Column('delivery_address_city', sa.String(length=100), nullable=False),
        sa.Column('delivery_address_state', sa.String(length=100), nullable=False),
        sa.Column('delivery_address_postal_code', sa.String(length=20), nullable=False),
        sa.Column('delivery_address_country', sa.String(length=100), nullable=False),
        sa.Column('delivery_notes', sa.String(length=500), nullable=True),
        sa.Column('subtotal_amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('subtotal_currency', sa.String(length=3), nullable=False),
        sa.Column('tax_amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('tax_currency', sa.String(length=3), nullable=False),
        sa.Column('delivery_fee_amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('delivery_fee_currency', sa.String(length=3), nullable=False),
        sa.Column('tip_amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('tip_currency', sa.String(length=3), nullable=False),
        sa.Column('total_amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('total_currency', sa.String(length=3), nullable=False),
        sa.Column('cancellation_reason', sa.String(length=500), nullable=True),
        sa.Column('placed_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('confirmed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('preparing_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ready_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('picked_up_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('delivered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('order_number'),
        schema='orders'
    )
    op.create_index('ix_orders_orders_restaurant_id', 'orders', ['restaurant_id'], unique=False, schema='orders')
    op.create_index('ix_orders_orders_customer_id', 'orders', ['customer_id'], unique=False, schema='orders')
    op.create_index('ix_orders_orders_order_number', 'orders', ['order_number'], unique=True, schema='orders')
    op.create_index('ix_orders_orders_status', 'orders', ['status'], unique=False, schema='orders')
    op.create_index('ix_orders_orders_placed_at', 'orders', ['placed_at'], unique=False, schema='orders')

    # 4. Create orders.order_items table
    op.create_table(
        'order_items',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('order_id', sa.UUID(), nullable=False),
        sa.Column('menu_item_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('price_amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('price_currency', sa.String(length=3), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('special_instructions', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['orders.orders.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='orders'
    )
    op.create_index('ix_orders_order_items_order_id', 'order_items', ['order_id'], unique=False, schema='orders')

    # 5. Enable RLS on orders and carts (tenant-scoped by restaurant_id)
    op.execute("CALL enable_tenant_rls('orders', 'orders', 'restaurant_id')")
    op.execute("CALL enable_tenant_rls('orders', 'carts', 'restaurant_id')")


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_isolation_policy ON orders.orders")
    op.execute("ALTER TABLE orders.orders DISABLE ROW LEVEL SECURITY")

    op.execute("DROP POLICY IF EXISTS tenant_isolation_policy ON orders.carts")
    op.execute("ALTER TABLE orders.carts DISABLE ROW LEVEL SECURITY")

    op.drop_table('order_items', schema='orders')
    op.drop_table('orders', schema='orders')
    op.drop_table('cart_items', schema='orders')
    op.drop_table('carts', schema='orders')
