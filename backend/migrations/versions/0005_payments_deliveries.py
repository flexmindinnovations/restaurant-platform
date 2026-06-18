"""payments_deliveries

Revision ID: 0005
Revises: 0004
Create Date: 2026-06-18 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0005'
down_revision: Union[str, None] = '0004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create payments.payment_methods
    op.create_table(
        'payment_methods',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('customer_id', sa.UUID(), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('last_four', sa.String(length=4), nullable=True),
        sa.Column('brand', sa.String(length=50), nullable=True),
        sa.Column('is_default', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('token', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        schema='payments'
    )
    op.create_index('ix_payments_payment_methods_customer_id', 'payment_methods', ['customer_id'], unique=False, schema='payments')

    # 2. Create payments.payments
    op.create_table(
        'payments',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('order_id', sa.UUID(), nullable=False),
        sa.Column('customer_id', sa.UUID(), nullable=False),
        sa.Column('restaurant_id', sa.UUID(), nullable=False),
        sa.Column('amount_cents', sa.Integer(), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('payment_method_type', sa.String(length=50), nullable=False),
        sa.Column('payment_method_id', sa.UUID(), nullable=True),
        sa.Column('gateway_transaction_id', sa.String(length=255), nullable=True),
        sa.Column('gateway_response', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('failure_reason', sa.String(length=255), nullable=True),
        sa.Column('captured_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('refunded_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        schema='payments'
    )
    op.create_index('ix_payments_payments_order_id', 'payments', ['order_id'], unique=False, schema='payments')
    op.create_index('ix_payments_payments_customer_id', 'payments', ['customer_id'], unique=False, schema='payments')
    op.create_index('ix_payments_payments_status', 'payments', ['status'], unique=False, schema='payments')

    # 3. Create deliveries.deliveries
    op.create_table(
        'deliveries',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('order_id', sa.UUID(), nullable=False),
        sa.Column('restaurant_id', sa.UUID(), nullable=False),
        sa.Column('partner_id', sa.UUID(), nullable=True),
        sa.Column('pickup_address', sa.String(length=255), nullable=False),
        sa.Column('delivery_address', sa.String(length=255), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('estimated_pickup_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('actual_pickup_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('estimated_delivery_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('actual_delivery_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('distance_km', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('proof_of_delivery_url', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        schema='deliveries'
    )
    op.create_index('ix_deliveries_deliveries_order_id', 'deliveries', ['order_id'], unique=False, schema='deliveries')
    op.create_index('ix_deliveries_deliveries_partner_id', 'deliveries', ['partner_id'], unique=False, schema='deliveries')
    op.create_index('ix_deliveries_deliveries_status', 'deliveries', ['status'], unique=False, schema='deliveries')

    # 4. Create deliveries.delivery_partners
    op.create_table(
        'delivery_partners',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('account_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=50), nullable=False),
        sa.Column('vehicle_type', sa.String(length=50), nullable=False),
        sa.Column('is_online', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('is_available', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('rating_avg', sa.Numeric(precision=3, scale=2), server_default='5.00', nullable=False),
        sa.Column('total_deliveries', sa.Integer(), server_default='0', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        schema='deliveries'
    )
    op.create_index('ix_deliveries_delivery_partners_account_id', 'delivery_partners', ['account_id'], unique=False, schema='deliveries')

    # 5. Create notifications.notifications
    op.create_table(
        'notifications',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('recipient_id', sa.UUID(), nullable=False),
        sa.Column('channel', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('body', sa.String(length=1000), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_message', sa.String(length=1000), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        schema='notifications'
    )
    op.create_index('ix_notifications_notifications_recipient_id', 'notifications', ['recipient_id'], unique=False, schema='notifications')
    op.create_index('ix_notifications_notifications_status', 'notifications', ['status'], unique=False, schema='notifications')

    # 6. Add PostGIS geography columns
    op.execute("ALTER TABLE deliveries.deliveries ADD COLUMN current_location geography(Point, 4326)")
    op.execute("ALTER TABLE deliveries.deliveries ADD COLUMN pickup_location geography(Point, 4326)")
    op.execute("ALTER TABLE deliveries.delivery_partners ADD COLUMN current_location geography(Point, 4326)")

    # 7. Enable RLS isolated by restaurant_id (tenant-scoped)
    op.execute("CALL enable_tenant_rls('payments', 'payments', 'restaurant_id')")
    op.execute("CALL enable_tenant_rls('deliveries', 'deliveries', 'restaurant_id')")


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_isolation_policy ON payments.payments")
    op.execute("ALTER TABLE payments.payments DISABLE ROW LEVEL SECURITY")

    op.execute("DROP POLICY IF EXISTS tenant_isolation_policy ON deliveries.deliveries")
    op.execute("ALTER TABLE deliveries.deliveries DISABLE ROW LEVEL SECURITY")

    op.drop_table('notifications', schema='notifications')
    op.drop_table('delivery_partners', schema='deliveries')
    op.drop_table('deliveries', schema='deliveries')
    op.drop_table('payments', schema='payments')
    op.drop_table('payment_methods', schema='payments')
