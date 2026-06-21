import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from modules.analytics.application.queries.get_platform_dashboard import (
    GetPlatformDashboardHandler,
    GetPlatformDashboardQuery,
)
from modules.analytics.application.queries.get_restaurant_dashboard import (
    GetRestaurantDashboardHandler,
    GetRestaurantDashboardQuery,
)
from modules.analytics.application.queries.get_revenue_breakdown import (
    COMMISSION_RATE,
    DELIVERY_RATE,
    GetRevenueBreakdownHandler,
    GetRevenueBreakdownQuery,
)
from modules.analytics.domain.entities.analytics_snapshot import (
    CustomerStats,
    DailyOrderStats,
    DeliveryStats,
    PeakHour,
    PlatformDashboard,
    PopularItem,
    RestaurantDashboard,
    RevenueBreakdown,
    TopRestaurant,
)
from modules.analytics.domain.value_objects.metric_type import MetricType
from modules.analytics.domain.value_objects.time_range import TimeRange

# --- Helpers ---

TODAY = datetime.now(UTC).date()
LAST_WEEK = TODAY - timedelta(days=7)
RESTAURANT_ID = uuid.uuid4()


def _make_daily_stats(count: int = 3) -> list[DailyOrderStats]:
    return [
        DailyOrderStats(
            date=TODAY - timedelta(days=i),
            order_count=10 + i,
            revenue=Decimal("500") + Decimal(str(i * 100)),
            average_order_value=Decimal("50.00"),
        )
        for i in range(count)
    ]


def _make_popular_items(count: int = 3) -> list[PopularItem]:
    return [
        PopularItem(
            menu_item_id=uuid.uuid4(),
            name=f"Item {i + 1}",
            order_count=20 - i * 5,
            total_revenue=Decimal("200") - Decimal(str(i * 50)),
        )
        for i in range(count)
    ]


def _make_peak_hours() -> list[PeakHour]:
    return [
        PeakHour(hour=12, order_count=50, average_revenue=Decimal("45.00")),
        PeakHour(hour=18, order_count=45, average_revenue=Decimal("55.00")),
        PeakHour(hour=19, order_count=40, average_revenue=Decimal("52.00")),
    ]


def _make_delivery_stats() -> DeliveryStats:
    return DeliveryStats(
        total_deliveries=100,
        average_delivery_minutes=Decimal("28.5"),
        on_time_percentage=Decimal("92.3"),
    )


def _make_customer_stats() -> CustomerStats:
    return CustomerStats(
        total_customers=500,
        new_customers=150,
        returning_customers=350,
        retention_rate=Decimal("70.0"),
    )


def _make_top_restaurants(count: int = 3) -> list[TopRestaurant]:
    return [
        TopRestaurant(
            restaurant_id=uuid.uuid4(),
            name=f"Restaurant {i + 1}",
            order_count=100 - i * 20,
            revenue=Decimal("5000") - Decimal(str(i * 1000)),
            average_rating=Decimal("4.5") - Decimal(str(i)) / Decimal("10"),
        )
        for i in range(count)
    ]


# --- Domain: Value Objects ---


@pytest.mark.unit
def test_time_range_values():
    assert TimeRange.TODAY == "TODAY"
    assert TimeRange.LAST_7_DAYS == "LAST_7_DAYS"
    assert TimeRange.LAST_30_DAYS == "LAST_30_DAYS"
    assert TimeRange.LAST_90_DAYS == "LAST_90_DAYS"
    assert TimeRange.CUSTOM == "CUSTOM"


@pytest.mark.unit
def test_metric_type_values():
    assert MetricType.ORDER_COUNT == "ORDER_COUNT"
    assert MetricType.REVENUE == "REVENUE"
    assert MetricType.AVERAGE_ORDER_VALUE == "AVERAGE_ORDER_VALUE"
    assert MetricType.AVERAGE_DELIVERY_TIME == "AVERAGE_DELIVERY_TIME"
    assert MetricType.CUSTOMER_COUNT == "CUSTOMER_COUNT"


# --- Domain: Data classes ---


@pytest.mark.unit
def test_daily_order_stats_creation():
    stats = DailyOrderStats(
        date=TODAY,
        order_count=42,
        revenue=Decimal("2100.50"),
        average_order_value=Decimal("50.01"),
    )
    assert stats.order_count == 42
    assert stats.revenue == Decimal("2100.50")
    assert stats.currency == "INR"


@pytest.mark.unit
def test_popular_item_creation():
    item = PopularItem(
        menu_item_id=uuid.uuid4(),
        name="Margherita Pizza",
        order_count=150,
        total_revenue=Decimal("2250.00"),
    )
    assert item.name == "Margherita Pizza"
    assert item.order_count == 150


@pytest.mark.unit
def test_peak_hour_creation():
    peak = PeakHour(hour=12, order_count=50, average_revenue=Decimal("45.00"))
    assert peak.hour == 12
    assert peak.order_count == 50


@pytest.mark.unit
def test_delivery_stats_creation():
    stats = _make_delivery_stats()
    assert stats.total_deliveries == 100
    assert stats.average_delivery_minutes == Decimal("28.5")
    assert stats.on_time_percentage == Decimal("92.3")


@pytest.mark.unit
def test_customer_stats_creation():
    stats = _make_customer_stats()
    assert stats.total_customers == 500
    assert stats.new_customers == 150
    assert stats.returning_customers == 350
    assert stats.retention_rate == Decimal("70.0")


@pytest.mark.unit
def test_restaurant_dashboard_creation():
    dashboard = RestaurantDashboard(
        restaurant_id=RESTAURANT_ID,
        daily_stats=_make_daily_stats(),
        popular_items=_make_popular_items(),
        peak_hours=_make_peak_hours(),
        delivery_stats=_make_delivery_stats(),
        total_orders=33,
        total_revenue=Decimal("1800"),
        average_rating=Decimal("4.5"),
    )
    assert dashboard.restaurant_id == RESTAURANT_ID
    assert len(dashboard.daily_stats) == 3
    assert len(dashboard.popular_items) == 3
    assert len(dashboard.peak_hours) == 3
    assert dashboard.delivery_stats is not None


@pytest.mark.unit
def test_platform_dashboard_creation():
    dashboard = PlatformDashboard(
        total_restaurants=50,
        total_orders=1000,
        total_revenue=Decimal("50000"),
        total_customers=500,
        daily_stats=_make_daily_stats(),
        customer_stats=_make_customer_stats(),
        delivery_stats=_make_delivery_stats(),
        top_restaurants=_make_top_restaurants(),
    )
    assert dashboard.total_restaurants == 50
    assert dashboard.total_orders == 1000
    assert len(dashboard.top_restaurants) == 3


@pytest.mark.unit
def test_revenue_breakdown_creation():
    breakdown = RevenueBreakdown(
        total_revenue=Decimal("50000"),
        commission_revenue=Decimal("7500"),
        delivery_revenue=Decimal("5000"),
        daily_revenue=_make_daily_stats(),
        top_restaurants=_make_top_restaurants(),
    )
    assert breakdown.total_revenue == Decimal("50000")
    assert breakdown.commission_revenue == Decimal("7500")


@pytest.mark.unit
def test_top_restaurant_creation():
    restaurant = TopRestaurant(
        restaurant_id=uuid.uuid4(),
        name="Best Burger",
        order_count=200,
        revenue=Decimal("10000"),
        average_rating=Decimal("4.8"),
    )
    assert restaurant.name == "Best Burger"
    assert restaurant.average_rating == Decimal("4.8")


# --- Application: GetRestaurantDashboardHandler ---


@pytest.mark.unit
@pytest.mark.asyncio
async def test_restaurant_dashboard_handler():
    repo = AsyncMock()
    daily = _make_daily_stats(2)
    repo.get_daily_order_stats.return_value = daily
    repo.get_popular_items.return_value = _make_popular_items(2)
    repo.get_peak_hours.return_value = _make_peak_hours()
    repo.get_delivery_stats.return_value = _make_delivery_stats()
    repo.get_restaurant_average_rating.return_value = 4.5

    handler = GetRestaurantDashboardHandler(repo)
    result = await handler.handle(
        GetRestaurantDashboardQuery(restaurant_id=RESTAURANT_ID, start_date=LAST_WEEK, end_date=TODAY)
    )

    assert result.restaurant_id == RESTAURANT_ID
    assert result.total_orders == sum(d.order_count for d in daily)
    assert result.total_revenue == sum(d.revenue for d in daily)
    assert result.average_rating == Decimal("4.5")
    assert len(result.popular_items) == 2
    assert len(result.peak_hours) == 3
    repo.get_daily_order_stats.assert_called_once()
    repo.get_popular_items.assert_called_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_restaurant_dashboard_handler_empty_data():
    repo = AsyncMock()
    repo.get_daily_order_stats.return_value = []
    repo.get_popular_items.return_value = []
    repo.get_peak_hours.return_value = []
    repo.get_delivery_stats.return_value = DeliveryStats(
        total_deliveries=0, average_delivery_minutes=Decimal("0"), on_time_percentage=Decimal("0")
    )
    repo.get_restaurant_average_rating.return_value = 0.0

    handler = GetRestaurantDashboardHandler(repo)
    result = await handler.handle(
        GetRestaurantDashboardQuery(restaurant_id=RESTAURANT_ID, start_date=LAST_WEEK, end_date=TODAY)
    )

    assert result.total_orders == 0
    assert result.total_revenue == Decimal("0")
    assert result.average_rating == Decimal("0.0")


# --- Application: GetPlatformDashboardHandler ---


@pytest.mark.unit
@pytest.mark.asyncio
async def test_platform_dashboard_handler():
    repo = AsyncMock()
    daily = _make_daily_stats(3)
    repo.get_daily_order_stats.return_value = daily
    repo.get_customer_stats.return_value = _make_customer_stats()
    repo.get_delivery_stats.return_value = _make_delivery_stats()
    repo.get_top_restaurants.return_value = _make_top_restaurants()
    repo.get_total_restaurants.return_value = 50
    repo.get_total_customers.return_value = 500

    handler = GetPlatformDashboardHandler(repo)
    result = await handler.handle(GetPlatformDashboardQuery(start_date=LAST_WEEK, end_date=TODAY))

    assert result.total_restaurants == 50
    assert result.total_customers == 500
    assert result.total_orders == sum(d.order_count for d in daily)
    assert result.total_revenue == sum(d.revenue for d in daily)
    assert len(result.top_restaurants) == 3
    assert result.customer_stats is not None
    assert result.delivery_stats is not None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_platform_dashboard_handler_empty():
    repo = AsyncMock()
    repo.get_daily_order_stats.return_value = []
    repo.get_customer_stats.return_value = CustomerStats(
        total_customers=0, new_customers=0, returning_customers=0, retention_rate=Decimal("0")
    )
    repo.get_delivery_stats.return_value = DeliveryStats(
        total_deliveries=0, average_delivery_minutes=Decimal("0"), on_time_percentage=Decimal("0")
    )
    repo.get_top_restaurants.return_value = []
    repo.get_total_restaurants.return_value = 0
    repo.get_total_customers.return_value = 0

    handler = GetPlatformDashboardHandler(repo)
    result = await handler.handle(GetPlatformDashboardQuery(start_date=LAST_WEEK, end_date=TODAY))

    assert result.total_orders == 0
    assert result.total_revenue == Decimal("0")


# --- Application: GetRevenueBreakdownHandler ---


@pytest.mark.unit
@pytest.mark.asyncio
async def test_revenue_breakdown_handler():
    repo = AsyncMock()
    daily = _make_daily_stats(2)
    repo.get_daily_order_stats.return_value = daily
    repo.get_top_restaurants.return_value = _make_top_restaurants()

    handler = GetRevenueBreakdownHandler(repo)
    result = await handler.handle(GetRevenueBreakdownQuery(start_date=LAST_WEEK, end_date=TODAY))

    total = sum(d.revenue for d in daily)
    assert result.total_revenue == total
    assert result.commission_revenue == (total * COMMISSION_RATE).quantize(Decimal("0.01"))
    assert result.delivery_revenue == (total * DELIVERY_RATE).quantize(Decimal("0.01"))
    assert len(result.top_restaurants) == 3


@pytest.mark.unit
@pytest.mark.asyncio
async def test_revenue_breakdown_handler_zero():
    repo = AsyncMock()
    repo.get_daily_order_stats.return_value = []
    repo.get_top_restaurants.return_value = []

    handler = GetRevenueBreakdownHandler(repo)
    result = await handler.handle(GetRevenueBreakdownQuery(start_date=LAST_WEEK, end_date=TODAY))

    assert result.total_revenue == Decimal("0")
    assert result.commission_revenue == Decimal("0.00")
    assert result.delivery_revenue == Decimal("0.00")
