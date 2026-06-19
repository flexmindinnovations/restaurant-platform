import uuid
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from modules.analytics.application.ports.analytics_repository import AnalyticsRepository
from modules.analytics.domain.entities.analytics_snapshot import RestaurantDashboard


@dataclass(frozen=True)
class GetRestaurantDashboardQuery:
    restaurant_id: uuid.UUID
    start_date: date
    end_date: date


class GetRestaurantDashboardHandler:
    def __init__(self, analytics_repo: AnalyticsRepository) -> None:
        self._analytics_repo = analytics_repo

    async def handle(self, query: GetRestaurantDashboardQuery) -> RestaurantDashboard:
        daily_stats = await self._analytics_repo.get_daily_order_stats(
            query.start_date, query.end_date, restaurant_id=query.restaurant_id
        )
        popular_items = await self._analytics_repo.get_popular_items(
            query.start_date, query.end_date, query.restaurant_id
        )
        peak_hours = await self._analytics_repo.get_peak_hours(query.start_date, query.end_date, query.restaurant_id)
        delivery_stats = await self._analytics_repo.get_delivery_stats(
            query.start_date, query.end_date, restaurant_id=query.restaurant_id
        )
        avg_rating = await self._analytics_repo.get_restaurant_average_rating(query.restaurant_id)

        total_orders = sum(d.order_count for d in daily_stats)
        total_revenue = sum((d.revenue for d in daily_stats), Decimal("0"))

        return RestaurantDashboard(
            restaurant_id=query.restaurant_id,
            daily_stats=daily_stats,
            popular_items=popular_items,
            peak_hours=peak_hours,
            delivery_stats=delivery_stats,
            total_orders=total_orders,
            total_revenue=total_revenue,
            average_rating=Decimal(str(avg_rating)),
        )
