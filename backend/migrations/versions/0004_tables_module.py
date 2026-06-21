"""tables_module

Revision ID: 0004
Revises: 0003
Create Date: 2026-06-21 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '0004'
down_revision: Union[str, None] = '0003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS tables")

    # 1. sections
    op.create_table(
        'sections',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('restaurant_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('display_order', sa.Integer(), server_default='0', nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        schema='tables',
    )
    op.create_index('ix_tables_sections_restaurant_id', 'sections', ['restaurant_id'], unique=False, schema='tables')

    # 2. tables
    op.create_table(
        'tables',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('restaurant_id', sa.UUID(), nullable=False),
        sa.Column('section_id', sa.UUID(), nullable=True),
        sa.Column('number', sa.String(length=20), nullable=False),
        sa.Column('capacity_min', sa.Integer(), server_default='1', nullable=False),
        sa.Column('capacity_max', sa.Integer(), server_default='1', nullable=False),
        sa.Column('shape', sa.String(length=20), server_default="'RECTANGULAR'", nullable=False),
        sa.Column('position_x', sa.Integer(), server_default='0', nullable=False),
        sa.Column('position_y', sa.Integer(), server_default='0', nullable=False),
        sa.Column('status', sa.String(length=20), server_default="'AVAILABLE'", nullable=False),
        sa.Column('turn_time_minutes', sa.Integer(), server_default='90', nullable=False),
        sa.Column('buffer_minutes', sa.Integer(), server_default='15', nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['section_id'], ['tables.sections.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('restaurant_id', 'number', name='uq_tables_restaurant_id_number'),
        schema='tables',
    )
    op.create_index('ix_tables_tables_restaurant_id', 'tables', ['restaurant_id'], unique=False, schema='tables')
    op.create_index('ix_tables_tables_section_id', 'tables', ['section_id'], unique=False, schema='tables')

    # 3. reservations
    op.create_table(
        'reservations',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('restaurant_id', sa.UUID(), nullable=False),
        sa.Column('table_id', sa.UUID(), nullable=True),
        sa.Column('customer_id', sa.UUID(), nullable=True),
        sa.Column('customer_name', sa.String(length=255), nullable=False),
        sa.Column('customer_phone', sa.String(length=20), nullable=True),
        sa.Column('customer_email', sa.String(length=255), nullable=True),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('start_time', sa.Time(), nullable=False),
        sa.Column('end_time', sa.Time(), nullable=False),
        sa.Column('party_size', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), server_default="'PENDING'", nullable=False),
        sa.Column('special_requests', sa.Text(), nullable=True),
        sa.Column('internal_notes', sa.Text(), nullable=True),
        sa.Column('hold_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('seated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancellation_reason', sa.Text(), nullable=True),
        sa.Column('source', sa.String(length=20), server_default="'PLATFORM'", nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['table_id'], ['tables.tables.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        schema='tables',
    )
    op.create_index(
        'ix_tables_reservations_restaurant_id', 'reservations', ['restaurant_id'], unique=False, schema='tables'
    )
    op.create_index('ix_tables_reservations_date', 'reservations', ['date'], unique=False, schema='tables')
    op.create_index(
        'ix_tables_reservations_customer_id', 'reservations', ['customer_id'], unique=False, schema='tables'
    )
    op.create_index('ix_tables_reservations_table_id', 'reservations', ['table_id'], unique=False, schema='tables')

    # 4. waitlist_entries
    op.create_table(
        'waitlist_entries',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('restaurant_id', sa.UUID(), nullable=False),
        sa.Column('customer_name', sa.String(length=255), nullable=False),
        sa.Column('customer_phone', sa.String(length=20), nullable=False),
        sa.Column('customer_id', sa.UUID(), nullable=True),
        sa.Column('party_size', sa.Integer(), nullable=False),
        sa.Column('estimated_wait_minutes', sa.Integer(), server_default='0', nullable=False),
        sa.Column('queue_position', sa.Integer(), server_default='0', nullable=False),
        sa.Column('status', sa.String(length=20), server_default="'WAITING'", nullable=False),
        sa.Column('preferred_section', sa.UUID(), nullable=True),
        sa.Column('special_requests', sa.Text(), nullable=True),
        sa.Column('notified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('seated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['preferred_section'], ['tables.sections.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        schema='tables',
    )
    op.create_index(
        'ix_tables_waitlist_entries_restaurant_id', 'waitlist_entries', ['restaurant_id'],
        unique=False, schema='tables',
    )

    # 5. Enable RLS
    op.execute("CALL enable_tenant_rls('tables', 'sections', 'restaurant_id')")
    op.execute("CALL enable_tenant_rls('tables', 'tables', 'restaurant_id')")
    op.execute("CALL enable_tenant_rls('tables', 'reservations', 'restaurant_id')")
    op.execute("CALL enable_tenant_rls('tables', 'waitlist_entries', 'restaurant_id')")


def downgrade() -> None:
    for table_name in ['waitlist_entries', 'reservations', 'tables', 'sections']:
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation_policy ON tables.{table_name}")
        op.execute(f"ALTER TABLE tables.{table_name} DISABLE ROW LEVEL SECURITY")

    op.drop_table('waitlist_entries', schema='tables')
    op.drop_table('reservations', schema='tables')
    op.drop_table('tables', schema='tables')
    op.drop_table('sections', schema='tables')

    op.execute("DROP SCHEMA IF EXISTS tables CASCADE")
