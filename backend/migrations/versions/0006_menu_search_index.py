"""menu_search_index — pg_trgm GIN index on menu_items

Revision ID: 0006
Revises: 0005
Create Date: 2026-06-18 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '0006'
down_revision: Union[str, None] = '0005'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_menu_items_search_trgm
        ON menus.menu_items
        USING gin ((coalesce(name, '') || ' ' || coalesce(description, '')) gin_trgm_ops)
    """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS menus.ix_menu_items_search_trgm")
