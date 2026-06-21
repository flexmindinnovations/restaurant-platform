import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from modules.analytics.application.ports.analytics_repository import AnalyticsRepository
from modules.analytics.domain.entities.analytics_snapshot import (
    CustomerStats,
    DailyOrderStats,
    DeliveryStats,
    PeakHour,
    PopularItem,
    TopRestaurant,
)


class SqlAlchemyAnalyticsRepository(AnalyticsRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_daily_order_stats(
        self, start_date: date, end_date: date, restaurant_id: uuid.UUID | None = None
    ) -> list[DailyOrderStats]:
        restaurant_filter = "AND o.restaurant_id = :restaurant_id" if restaurant_id else ""
        params: dict = {"start_date": start_date, "end_date": end_date}
        if restaurant_id:
            params["restaurant_id"] = str(restaurant_id)

        query = f"""
            SELECT
                DATE(o.placed_at) AS day,
                COUNT(*) AS order_count,
                COALESCE(SUM(o.total_amount), 0) AS revenue,
                COALESCE(AVG(o.total_amount), 0) AS avg_order_value,
                COALESCE(MAX(o.total_currency), 'INR') AS currency
            FROM orders.orders o
            WHERE o.status NOT IN ('CANCELLED')
                AND DATE(o.placed_at) BETWEEN :start_date AND :end_date
                {restaurant_filter}
            GROUP BY DATE(o.placed_at)
            ORDER BY day
        """  # noqa: S608
        result = await self._session.execute(
            text(query),
            params,
        )
        return [
            DailyOrderStats(
                date=row.day,
                order_count=row.order_count,
                revenue=Decimal(str(row.revenue)),
                average_order_value=Decimal(str(row.avg_order_value)).quantize(Decimal("0.01")),
                currency=row.currency,
            )
            for row in result.fetchall()
        ]

    async def get_popular_items(
        self, start_date: date, end_date: date, restaurant_id: uuid.UUID, limit: int = 10
    ) -> list[PopularItem]:
        result = await self._session.execute(
            text("""
                SELECT
                    oi.menu_item_id,
                    oi.name,
                    SUM(oi.quantity) AS order_count,
                    SUM(oi.price_amount * oi.quantity) AS total_revenue,
                    COALESCE(MAX(oi.price_currency), 'INR') AS currency
                FROM orders.order_items oi
                JOIN orders.orders o ON o.id = oi.order_id
                WHERE o.restaurant_id = :restaurant_id
                    AND o.status NOT IN ('CANCELLED')
                    AND DATE(o.placed_at) BETWEEN :start_date AND :end_date
                GROUP BY oi.menu_item_id, oi.name
                ORDER BY order_count DESC
                LIMIT :limit
            """),
            {
                "restaurant_id": str(restaurant_id),
                "start_date": start_date,
                "end_date": end_date,
                "limit": limit,
            },
        )
        return [
            PopularItem(
                menu_item_id=row.menu_item_id,
                name=row.name,
                order_count=int(row.order_count),
                total_revenue=Decimal(str(row.total_revenue)),
                currency=row.currency,
            )
            for row in result.fetchall()
        ]

    async def get_peak_hours(self, start_date: date, end_date: date, restaurant_id: uuid.UUID) -> list[PeakHour]:
        result = await self._session.execute(
            text("""
                SELECT
                    EXTRACT(HOUR FROM o.placed_at) AS hour,
                    COUNT(*) AS order_count,
                    COALESCE(AVG(o.total_amount), 0) AS avg_revenue,
                    COALESCE(MAX(o.total_currency), 'INR') AS currency
                FROM orders.orders o
                WHERE o.restaurant_id = :restaurant_id
                    AND o.status NOT IN ('CANCELLED')
                    AND DATE(o.placed_at) BETWEEN :start_date AND :end_date
                GROUP BY EXTRACT(HOUR FROM o.placed_at)
                ORDER BY order_count DESC
            """),
            {"restaurant_id": str(restaurant_id), "start_date": start_date, "end_date": end_date},
        )
        return [
            PeakHour(
                hour=int(row.hour),
                order_count=row.order_count,
                average_revenue=Decimal(str(row.avg_revenue)).quantize(Decimal("0.01")),
                currency=row.currency,
            )
            for row in result.fetchall()
        ]

    async def get_delivery_stats(
        self, start_date: date, end_date: date, restaurant_id: uuid.UUID | None = None
    ) -> DeliveryStats:
        restaurant_filter = "AND d.restaurant_id = :restaurant_id" if restaurant_id else ""
        params: dict = {"start_date": start_date, "end_date": end_date}
        if restaurant_id:
            params["restaurant_id"] = str(restaurant_id)

        query = f"""
            SELECT
                COUNT(*) AS total_deliveries,
                COALESCE(AVG(
                    EXTRACT(EPOCH FROM (d.actual_delivery_time - d.actual_pickup_time)) / 60
                ), 0) AS avg_delivery_minutes,
                COALESCE(
                    COUNT(*) FILTER (
                        WHERE d.actual_delivery_time <= d.estimated_delivery_time
                    ) * 100.0 / NULLIF(COUNT(*), 0),
                    0
                ) AS on_time_pct
            FROM deliveries.deliveries d
            WHERE d.status = 'DELIVERED'
                AND DATE(d.created_at) BETWEEN :start_date AND :end_date
                {restaurant_filter}
        """  # noqa: S608
        result = await self._session.execute(
            text(query),
            params,
        )
        row = result.fetchone()
        if not row:
            return DeliveryStats(
                total_deliveries=0,
                average_delivery_minutes=Decimal("0"),
                on_time_percentage=Decimal("0"),
            )
        return DeliveryStats(
            total_deliveries=row.total_deliveries,
            average_delivery_minutes=Decimal(str(row.avg_delivery_minutes)).quantize(Decimal("0.1")),
            on_time_percentage=Decimal(str(row.on_time_pct)).quantize(Decimal("0.1")),
        )

    async def get_customer_stats(self, start_date: date, end_date: date) -> CustomerStats:
        result = await self._session.execute(
            text("""
                WITH period_customers AS (
                    SELECT DISTINCT customer_id
                    FROM orders.orders
                    WHERE status NOT IN ('CANCELLED')
                        AND DATE(placed_at) BETWEEN :start_date AND :end_date
                ),
                prior_customers AS (
                    SELECT DISTINCT customer_id
                    FROM orders.orders
                    WHERE status NOT IN ('CANCELLED')
                        AND DATE(placed_at) < :start_date
                ),
                total AS (
                    SELECT COUNT(*) AS total_customers FROM period_customers
                ),
                returning_cust AS (
                    SELECT COUNT(*) AS returning_customers
                    FROM period_customers pc
                    WHERE EXISTS (SELECT 1 FROM prior_customers pr WHERE pr.customer_id = pc.customer_id)
                )
                SELECT
                    t.total_customers,
                    t.total_customers - r.returning_customers AS new_customers,
                    r.returning_customers,
                    CASE WHEN t.total_customers > 0
                        THEN r.returning_customers * 100.0 / t.total_customers
                        ELSE 0 END AS retention_rate
                FROM total t, returning_cust r
            """),
            {"start_date": start_date, "end_date": end_date},
        )
        row = result.fetchone()
        if not row:
            return CustomerStats(total_customers=0, new_customers=0, returning_customers=0, retention_rate=Decimal("0"))
        return CustomerStats(
            total_customers=row.total_customers,
            new_customers=row.new_customers,
            returning_customers=row.returning_customers,
            retention_rate=Decimal(str(row.retention_rate)).quantize(Decimal("0.1")),
        )

    async def get_top_restaurants(self, start_date: date, end_date: date, limit: int = 10) -> list[TopRestaurant]:
        result = await self._session.execute(
            text("""
                SELECT
                    o.restaurant_id,
                    r.name,
                    COUNT(*) AS order_count,
                    COALESCE(SUM(o.total_amount), 0) AS revenue,
                    COALESCE(AVG(rv.rating), 0) AS avg_rating,
                    COALESCE(MAX(o.total_currency), 'INR') AS currency
                FROM orders.orders o
                JOIN restaurants.restaurants r ON r.id = o.restaurant_id
                LEFT JOIN reviews.reviews rv ON rv.restaurant_id = o.restaurant_id
                WHERE o.status NOT IN ('CANCELLED')
                    AND DATE(o.placed_at) BETWEEN :start_date AND :end_date
                GROUP BY o.restaurant_id, r.name
                ORDER BY revenue DESC
                LIMIT :limit
            """),
            {"start_date": start_date, "end_date": end_date, "limit": limit},
        )
        return [
            TopRestaurant(
                restaurant_id=row.restaurant_id,
                name=row.name,
                order_count=row.order_count,
                revenue=Decimal(str(row.revenue)),
                average_rating=Decimal(str(row.avg_rating)).quantize(Decimal("0.1")),
                currency=row.currency,
            )
            for row in result.fetchall()
        ]

    async def get_total_restaurants(self) -> int:
        result = await self._session.execute(
            text("SELECT COUNT(*) AS cnt FROM restaurants.restaurants WHERE is_active = true")
        )
        row = result.fetchone()
        return row.cnt if row else 0

    async def get_total_customers(self) -> int:
        result = await self._session.execute(
            text("SELECT COUNT(DISTINCT customer_id) AS cnt FROM orders.orders WHERE status NOT IN ('CANCELLED')")
        )
        row = result.fetchone()
        return row.cnt if row else 0

    async def get_restaurant_average_rating(self, restaurant_id: uuid.UUID) -> float:
        result = await self._session.execute(
            text("""
                SELECT COALESCE(AVG(rating), 0) AS avg_rating
                FROM reviews.reviews
                WHERE restaurant_id = :restaurant_id
            """),
            {"restaurant_id": str(restaurant_id)},
        )
        row = result.fetchone()
        return float(row.avg_rating) if row else 0.0
