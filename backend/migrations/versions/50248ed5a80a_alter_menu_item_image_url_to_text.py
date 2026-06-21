"""alter_menu_item_image_url_to_text

Revision ID: 50248ed5a80a
Revises: 0011
Create Date: 2026-06-21 15:20:30.393292

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '50248ed5a80a'
down_revision: Union[str, None] = '0011'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        'menu_items',
        'image_url',
        existing_type=sa.String(length=500),
        type_=sa.Text(),
        existing_nullable=True,
        schema='menus'
    )


def downgrade() -> None:
    op.alter_column(
        'menu_items',
        'image_url',
        existing_type=sa.Text(),
        type_=sa.String(length=500),
        existing_nullable=True,
        schema='menus'
    )
