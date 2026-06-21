import uuid
from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class DailyOrderStatsResponse(BaseModel):
    date: date
    order_count: int
    revenue: Decimal
    average_order_value: Decimal
    currency: str = "INR"


class PopularItemResponse(BaseModel):
    menu_item_id: uuid.UUID
    name: str
    order_count: int
    total_revenue: Decimal
    currency: str = "INR"


class PeakHourResponse(BaseModel):
    hour: int
    order_count: int
    average_revenue: Decimal
    currency: str = "INR"


class DeliveryStatsResponse(BaseModel):
    total_deliveries: int
    average_delivery_minutes: Decimal
    on_time_percentage: Decimal


class CustomerStatsResponse(BaseModel):
    total_customers: int
    new_customers: int
    returning_customers: int
    retention_rate: Decimal


class TopRestaurantResponse(BaseModel):
    restaurant_id: uuid.UUID
    name: str
    order_count: int
    revenue: Decimal
    average_rating: Decimal
    currency: str = "INR"


class RestaurantDashboardResponse(BaseModel):
    restaurant_id: uuid.UUID
    daily_stats: list[DailyOrderStatsResponse]
    popular_items: list[PopularItemResponse]
    peak_hours: list[PeakHourResponse]
    delivery_stats: DeliveryStatsResponse | None
    total_orders: int
    total_revenue: Decimal
    average_rating: Decimal
    currency: str = "INR"


class PlatformDashboardResponse(BaseModel):
    total_restaurants: int
    total_orders: int
    total_revenue: Decimal
    total_customers: int
    daily_stats: list[DailyOrderStatsResponse]
    customer_stats: CustomerStatsResponse | None
    delivery_stats: DeliveryStatsResponse | None
    top_restaurants: list[TopRestaurantResponse]
    currency: str = "INR"


class RevenueBreakdownResponse(BaseModel):
    total_revenue: Decimal
    commission_revenue: Decimal
    delivery_revenue: Decimal
    daily_revenue: list[DailyOrderStatsResponse]
    top_restaurants: list[TopRestaurantResponse]
    currency: str = "INR"
