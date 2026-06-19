from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from modules.analytics.application.ports.analytics_repository import AnalyticsRepository
from modules.analytics.domain.entities.analytics_snapshot import PlatformDashboard


@dataclass(frozen=True)
class GetPlatformDashboardQuery:
    start_date: date
    end_date: date


class GetPlatformDashboardHandler:
    def __init__(self, analytics_repo: AnalyticsRepository) -> None:
        self._analytics_repo = analytics_repo

    async def handle(self, query: GetPlatformDashboardQuery) -> PlatformDashboard:
        daily_stats = await self._analytics_repo.get_daily_order_stats(query.start_date, query.end_date)
        customer_stats = await self._analytics_repo.get_customer_stats(query.start_date, query.end_date)
        delivery_stats = await self._analytics_repo.get_delivery_stats(query.start_date, query.end_date)
        top_restaurants = await self._analytics_repo.get_top_restaurants(query.start_date, query.end_date)
        total_restaurants = await self._analytics_repo.get_total_restaurants()
        total_customers = await self._analytics_repo.get_total_customers()

        total_orders = sum(d.order_count for d in daily_stats)
        total_revenue = sum((d.revenue for d in daily_stats), Decimal("0"))

        return PlatformDashboard(
            total_restaurants=total_restaurants,
            total_orders=total_orders,
            total_revenue=total_revenue,
            total_customers=total_customers,
            daily_stats=daily_stats,
            customer_stats=customer_stats,
            delivery_stats=delivery_stats,
            top_restaurants=top_restaurants,
        )
