import uuid
from datetime import UTC, date, datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, Query

from modules.analytics.api.dependencies import (
    get_platform_dashboard_handler,
    get_restaurant_dashboard_handler,
    get_revenue_breakdown_handler,
)
from modules.analytics.api.schemas import (
    CustomerStatsResponse,
    DailyOrderStatsResponse,
    DeliveryStatsResponse,
    PeakHourResponse,
    PlatformDashboardResponse,
    PopularItemResponse,
    RestaurantDashboardResponse,
    RevenueBreakdownResponse,
    TopRestaurantResponse,
)
from modules.analytics.application.queries.get_platform_dashboard import (
    GetPlatformDashboardHandler,
    GetPlatformDashboardQuery,
)
from modules.analytics.application.queries.get_restaurant_dashboard import (
    GetRestaurantDashboardHandler,
    GetRestaurantDashboardQuery,
)
from modules.analytics.application.queries.get_revenue_breakdown import (
    GetRevenueBreakdownHandler,
    GetRevenueBreakdownQuery,
)
from shared.api.response import ResponseEnvelope
from shared.api.security import require_roles

router = APIRouter()

DEFAULT_DAYS = 30


def _daily_stats_response(stats: Any) -> list[DailyOrderStatsResponse]:
    return [
        DailyOrderStatsResponse(
            date=s.date,
            order_count=s.order_count,
            revenue=s.revenue,
            average_order_value=s.average_order_value,
            currency=s.currency,
        )
        for s in stats
    ]


def _top_restaurants_response(restaurants: Any) -> list[TopRestaurantResponse]:
    return [
        TopRestaurantResponse(
            restaurant_id=r.restaurant_id,
            name=r.name,
            order_count=r.order_count,
            revenue=r.revenue,
            average_rating=r.average_rating,
            currency=r.currency,
        )
        for r in restaurants
    ]


@router.get("/restaurant/{restaurant_id}/dashboard", response_model=ResponseEnvelope[RestaurantDashboardResponse])
async def get_restaurant_dashboard(
    restaurant_id: uuid.UUID,
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    _current_user: dict[str, Any] = Depends(require_roles("SUPER_ADMIN", "RESTAURANT_OWNER", "RESTAURANT_MANAGER")),
    handler: GetRestaurantDashboardHandler = Depends(get_restaurant_dashboard_handler),
) -> ResponseEnvelope[RestaurantDashboardResponse]:
    today = datetime.now(UTC).date()
    s = start_date or today - timedelta(days=DEFAULT_DAYS)
    e = end_date or today

    dashboard = await handler.handle(GetRestaurantDashboardQuery(restaurant_id=restaurant_id, start_date=s, end_date=e))

    delivery_stats = None
    if dashboard.delivery_stats:
        delivery_stats = DeliveryStatsResponse(
            total_deliveries=dashboard.delivery_stats.total_deliveries,
            average_delivery_minutes=dashboard.delivery_stats.average_delivery_minutes,
            on_time_percentage=dashboard.delivery_stats.on_time_percentage,
        )

    return ResponseEnvelope(
        data=RestaurantDashboardResponse(
            restaurant_id=dashboard.restaurant_id,
            daily_stats=_daily_stats_response(dashboard.daily_stats),
            popular_items=[
                PopularItemResponse(
                    menu_item_id=p.menu_item_id,
                    name=p.name,
                    order_count=p.order_count,
                    total_revenue=p.total_revenue,
                    currency=p.currency,
                )
                for p in dashboard.popular_items
            ],
            peak_hours=[
                PeakHourResponse(
                    hour=h.hour,
                    order_count=h.order_count,
                    average_revenue=h.average_revenue,
                    currency=h.currency,
                )
                for h in dashboard.peak_hours
            ],
            delivery_stats=delivery_stats,
            total_orders=dashboard.total_orders,
            total_revenue=dashboard.total_revenue,
            average_rating=dashboard.average_rating,
            currency=dashboard.currency,
        )
    )


@router.get("/platform", response_model=ResponseEnvelope[PlatformDashboardResponse])
async def get_platform_dashboard(
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    _current_user: dict[str, Any] = Depends(require_roles("SUPER_ADMIN")),
    handler: GetPlatformDashboardHandler = Depends(get_platform_dashboard_handler),
) -> ResponseEnvelope[PlatformDashboardResponse]:
    today = datetime.now(UTC).date()
    s = start_date or today - timedelta(days=DEFAULT_DAYS)
    e = end_date or today

    dashboard = await handler.handle(GetPlatformDashboardQuery(start_date=s, end_date=e))

    customer_stats = None
    if dashboard.customer_stats:
        customer_stats = CustomerStatsResponse(
            total_customers=dashboard.customer_stats.total_customers,
            new_customers=dashboard.customer_stats.new_customers,
            returning_customers=dashboard.customer_stats.returning_customers,
            retention_rate=dashboard.customer_stats.retention_rate,
        )

    delivery_stats = None
    if dashboard.delivery_stats:
        delivery_stats = DeliveryStatsResponse(
            total_deliveries=dashboard.delivery_stats.total_deliveries,
            average_delivery_minutes=dashboard.delivery_stats.average_delivery_minutes,
            on_time_percentage=dashboard.delivery_stats.on_time_percentage,
        )

    return ResponseEnvelope(
        data=PlatformDashboardResponse(
            total_restaurants=dashboard.total_restaurants,
            total_orders=dashboard.total_orders,
            total_revenue=dashboard.total_revenue,
            total_customers=dashboard.total_customers,
            daily_stats=_daily_stats_response(dashboard.daily_stats),
            customer_stats=customer_stats,
            delivery_stats=delivery_stats,
            top_restaurants=_top_restaurants_response(dashboard.top_restaurants),
            currency=dashboard.currency,
        )
    )


@router.get("/revenue", response_model=ResponseEnvelope[RevenueBreakdownResponse])
async def get_revenue_breakdown(
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    _current_user: dict[str, Any] = Depends(require_roles("SUPER_ADMIN")),
    handler: GetRevenueBreakdownHandler = Depends(get_revenue_breakdown_handler),
) -> ResponseEnvelope[RevenueBreakdownResponse]:
    today = datetime.now(UTC).date()
    s = start_date or today - timedelta(days=DEFAULT_DAYS)
    e = end_date or today

    breakdown = await handler.handle(GetRevenueBreakdownQuery(start_date=s, end_date=e))

    return ResponseEnvelope(
        data=RevenueBreakdownResponse(
            total_revenue=breakdown.total_revenue,
            commission_revenue=breakdown.commission_revenue,
            delivery_revenue=breakdown.delivery_revenue,
            daily_revenue=_daily_stats_response(breakdown.daily_revenue),
            top_restaurants=_top_restaurants_response(breakdown.top_restaurants),
            currency=breakdown.currency,
        )
    )
