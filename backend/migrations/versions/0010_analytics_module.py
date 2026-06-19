"""analytics_module — Analytics schema with materialized views for dashboards

Revision ID: 0010
Revises: 0009
Create Date: 2026-06-19 01:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

revision: str = '0010'
down_revision: Union[str, None] = '0009'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS analytics")

    op.execute("""
        CREATE MATERIALIZED VIEW analytics.mv_daily_order_stats AS
        SELECT
            DATE(o.placed_at) AS day,
            o.restaurant_id,
            COUNT(*) AS order_count,
            COALESCE(SUM(o.total_amount), 0) AS revenue,
            COALESCE(AVG(o.total_amount), 0) AS avg_order_value,
            COALESCE(MAX(o.total_currency), 'USD') AS currency
        FROM orders.orders o
        WHERE o.status NOT IN ('CANCELLED')
        GROUP BY DATE(o.placed_at), o.restaurant_id
        ORDER BY day
        WITH NO DATA
    """)

    op.execute("""
        CREATE UNIQUE INDEX idx_mv_daily_order_stats_day_restaurant
        ON analytics.mv_daily_order_stats (day, restaurant_id)
    """)

    op.execute("""
        CREATE MATERIALIZED VIEW analytics.mv_popular_items AS
        SELECT
            oi.menu_item_id,
            oi.name,
            o.restaurant_id,
            SUM(oi.quantity) AS total_quantity,
            SUM(oi.price_amount * oi.quantity) AS total_revenue,
            COALESCE(MAX(oi.price_currency), 'USD') AS currency
        FROM orders.order_items oi
        JOIN orders.orders o ON o.id = oi.order_id
        WHERE o.status NOT IN ('CANCELLED')
        GROUP BY oi.menu_item_id, oi.name, o.restaurant_id
        WITH NO DATA
    """)

    op.execute("""
        CREATE UNIQUE INDEX idx_mv_popular_items_restaurant_item
        ON analytics.mv_popular_items (restaurant_id, menu_item_id)
    """)

    op.execute("""
        CREATE MATERIALIZED VIEW analytics.mv_peak_hours AS
        SELECT
            o.restaurant_id,
            EXTRACT(HOUR FROM o.placed_at)::int AS hour,
            COUNT(*) AS order_count,
            COALESCE(AVG(o.total_amount), 0) AS avg_revenue,
            COALESCE(MAX(o.total_currency), 'USD') AS currency
        FROM orders.orders o
        WHERE o.status NOT IN ('CANCELLED')
        GROUP BY o.restaurant_id, EXTRACT(HOUR FROM o.placed_at)
        WITH NO DATA
    """)

    op.execute("""
        CREATE UNIQUE INDEX idx_mv_peak_hours_restaurant_hour
        ON analytics.mv_peak_hours (restaurant_id, hour)
    """)


def downgrade() -> None:
    op.execute("DROP MATERIALIZED VIEW IF EXISTS analytics.mv_peak_hours")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS analytics.mv_popular_items")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS analytics.mv_daily_order_stats")
    op.execute("DROP SCHEMA IF EXISTS analytics")
