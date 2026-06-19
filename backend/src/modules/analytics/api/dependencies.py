from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from modules.analytics.application.queries.get_platform_dashboard import GetPlatformDashboardHandler
from modules.analytics.application.queries.get_restaurant_dashboard import GetRestaurantDashboardHandler
from modules.analytics.application.queries.get_revenue_breakdown import GetRevenueBreakdownHandler
from modules.analytics.infrastructure.repositories.sqlalchemy_analytics_repository import (
    SqlAlchemyAnalyticsRepository,
)
from shared.infrastructure.database import get_session


def get_restaurant_dashboard_handler(
    session: AsyncSession = Depends(get_session),
) -> GetRestaurantDashboardHandler:
    repo = SqlAlchemyAnalyticsRepository(session)
    return GetRestaurantDashboardHandler(repo)


def get_platform_dashboard_handler(
    session: AsyncSession = Depends(get_session),
) -> GetPlatformDashboardHandler:
    repo = SqlAlchemyAnalyticsRepository(session)
    return GetPlatformDashboardHandler(repo)


def get_revenue_breakdown_handler(
    session: AsyncSession = Depends(get_session),
) -> GetRevenueBreakdownHandler:
    repo = SqlAlchemyAnalyticsRepository(session)
    return GetRevenueBreakdownHandler(repo)
