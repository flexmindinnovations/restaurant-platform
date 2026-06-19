from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from modules.analytics.application.ports.analytics_repository import AnalyticsRepository
from modules.analytics.domain.entities.analytics_snapshot import RevenueBreakdown

COMMISSION_RATE = Decimal("0.15")
DELIVERY_RATE = Decimal("0.10")


@dataclass(frozen=True)
class GetRevenueBreakdownQuery:
    start_date: date
    end_date: date


class GetRevenueBreakdownHandler:
    def __init__(self, analytics_repo: AnalyticsRepository) -> None:
        self._analytics_repo = analytics_repo

    async def handle(self, query: GetRevenueBreakdownQuery) -> RevenueBreakdown:
        daily_stats = await self._analytics_repo.get_daily_order_stats(query.start_date, query.end_date)
        top_restaurants = await self._analytics_repo.get_top_restaurants(query.start_date, query.end_date)

        total_revenue = sum((d.revenue for d in daily_stats), Decimal("0"))
        commission_revenue = (total_revenue * COMMISSION_RATE).quantize(Decimal("0.01"))
        delivery_revenue = (total_revenue * DELIVERY_RATE).quantize(Decimal("0.01"))

        return RevenueBreakdown(
            total_revenue=total_revenue,
            commission_revenue=commission_revenue,
            delivery_revenue=delivery_revenue,
            daily_revenue=daily_stats,
            top_restaurants=top_restaurants,
        )
