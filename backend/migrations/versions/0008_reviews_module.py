"""reviews_module — Review table with RLS

Revision ID: 0008
Revises: 0007
Create Date: 2026-06-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0008'
down_revision: Union[str, None] = '0007'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS reviews")

    op.create_table(
        'reviews',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('order_id', postgresql.UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('restaurant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=False, server_default=''),
        sa.Column('sentiment', sa.String(20), nullable=True),
        sa.Column('is_flagged', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('flag_reason', sa.String(500), nullable=True),
        sa.Column('reply', sa.Text(), nullable=True),
        sa.Column('replied_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('images', postgresql.ARRAY(sa.String(500)), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint('rating >= 1 AND rating <= 5', name='ck_reviews_rating_range'),
        schema='reviews',
    )

    op.create_index('ix_reviews_order_id', 'reviews', ['order_id'], schema='reviews')
    op.create_index('ix_reviews_customer_id', 'reviews', ['customer_id'], schema='reviews')
    op.create_index('ix_reviews_restaurant_id', 'reviews', ['restaurant_id'], schema='reviews')
    op.create_index('ix_reviews_is_flagged', 'reviews', ['is_flagged'], schema='reviews', postgresql_where=sa.text('is_flagged = true'))

    op.execute("ALTER TABLE reviews.reviews ENABLE ROW LEVEL SECURITY")
    op.execute("""
        CREATE POLICY reviews_tenant_isolation ON reviews.reviews
            USING (restaurant_id = current_setting('app.current_restaurant_id')::uuid)
    """)


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS reviews_tenant_isolation ON reviews.reviews")
    op.drop_table('reviews', schema='reviews')
    op.execute("DROP SCHEMA IF EXISTS reviews")
