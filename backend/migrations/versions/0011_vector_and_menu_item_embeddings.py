"""vector_and_menu_item_embeddings

Revision ID: 0011
Revises: 0010
Create Date: 2026-06-19 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0011'
down_revision: Union[str, None] = '0010'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Enable the vector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # 2. Create menus.menu_item_embeddings table
    op.create_table(
        'menu_item_embeddings',
        sa.Column('menu_item_id', sa.UUID(), nullable=False),
        sa.Column('embedding', sa.UserDefinedType('vector', 768), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['menu_item_id'], ['menus.menu_items.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('menu_item_id'),
        schema='menus'
    )


def downgrade() -> None:
    op.drop_table('menu_item_embeddings', schema='menus')
