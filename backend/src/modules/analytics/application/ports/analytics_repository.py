import uuid
from abc import ABC, abstractmethod
from datetime import date

from modules.analytics.domain.entities.analytics_snapshot import (
    CustomerStats,
    DailyOrderStats,
    DeliveryStats,
    PeakHour,
    PopularItem,
    TopRestaurant,
)


class AnalyticsRepository(ABC):
    @abstractmethod
    async def get_daily_order_stats(
        self, start_date: date, end_date: date, restaurant_id: uuid.UUID | None = None
    ) -> list[DailyOrderStats]: ...

    @abstractmethod
    async def get_popular_items(
        self, start_date: date, end_date: date, restaurant_id: uuid.UUID, limit: int = 10
    ) -> list[PopularItem]: ...

    @abstractmethod
    async def get_peak_hours(self, start_date: date, end_date: date, restaurant_id: uuid.UUID) -> list[PeakHour]: ...

    @abstractmethod
    async def get_delivery_stats(
        self, start_date: date, end_date: date, restaurant_id: uuid.UUID | None = None
    ) -> DeliveryStats: ...

    @abstractmethod
    async def get_customer_stats(self, start_date: date, end_date: date) -> CustomerStats: ...

    @abstractmethod
    async def get_top_restaurants(self, start_date: date, end_date: date, limit: int = 10) -> list[TopRestaurant]: ...

    @abstractmethod
    async def get_total_restaurants(self) -> int: ...

    @abstractmethod
    async def get_total_customers(self) -> int: ...

    @abstractmethod
    async def get_restaurant_average_rating(self, restaurant_id: uuid.UUID) -> float: ...
