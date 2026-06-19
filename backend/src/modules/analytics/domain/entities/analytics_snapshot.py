import uuid
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class DailyOrderStats:
    date: date
    order_count: int
    revenue: Decimal
    average_order_value: Decimal
    currency: str = "USD"


@dataclass(frozen=True)
class PopularItem:
    menu_item_id: uuid.UUID
    name: str
    order_count: int
    total_revenue: Decimal
    currency: str = "USD"


@dataclass(frozen=True)
class PeakHour:
    hour: int
    order_count: int
    average_revenue: Decimal
    currency: str = "USD"


@dataclass(frozen=True)
class DeliveryStats:
    total_deliveries: int
    average_delivery_minutes: Decimal
    on_time_percentage: Decimal


@dataclass(frozen=True)
class CustomerStats:
    total_customers: int
    new_customers: int
    returning_customers: int
    retention_rate: Decimal


@dataclass(frozen=True)
class RestaurantDashboard:
    restaurant_id: uuid.UUID
    daily_stats: list[DailyOrderStats] = field(default_factory=list)
    popular_items: list[PopularItem] = field(default_factory=list)
    peak_hours: list[PeakHour] = field(default_factory=list)
    delivery_stats: DeliveryStats | None = None
    total_orders: int = 0
    total_revenue: Decimal = Decimal("0")
    average_rating: Decimal = Decimal("0")
    currency: str = "USD"


@dataclass(frozen=True)
class PlatformDashboard:
    total_restaurants: int = 0
    total_orders: int = 0
    total_revenue: Decimal = Decimal("0")
    total_customers: int = 0
    daily_stats: list[DailyOrderStats] = field(default_factory=list)
    customer_stats: CustomerStats | None = None
    delivery_stats: DeliveryStats | None = None
    top_restaurants: list["TopRestaurant"] = field(default_factory=list)
    currency: str = "USD"


@dataclass(frozen=True)
class TopRestaurant:
    restaurant_id: uuid.UUID
    name: str
    order_count: int
    revenue: Decimal
    average_rating: Decimal
    currency: str = "USD"


@dataclass(frozen=True)
class RevenueBreakdown:
    total_revenue: Decimal
    commission_revenue: Decimal
    delivery_revenue: Decimal
    daily_revenue: list[DailyOrderStats] = field(default_factory=list)
    top_restaurants: list[TopRestaurant] = field(default_factory=list)
    currency: str = "USD"
