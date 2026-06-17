from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.config import get_settings
from app.observability import setup_logging, setup_telemetry
from modules.analytics.api.routes import router as analytics_router
from modules.deliveries.api.routes import router as deliveries_router
from modules.identity.api.routes import router as identity_router
from modules.menus.api.routes import router as menus_router
from modules.notifications.api.routes import router as notifications_router
from modules.orders.api.routes import router as orders_router
from modules.payments.api.routes import router as payments_router
from modules.promotions.api.routes import router as promotions_router
from modules.restaurants.api.routes import router as restaurants_router
from modules.reviews.api.routes import router as reviews_router
from modules.users.api.routes import router as users_router
from shared.api.errors import register_error_handlers
from shared.api.middleware.cors import setup_cors
from shared.api.middleware.request_id import RequestIDMiddleware
from shared.infrastructure.database import close_engine, get_session_factory, init_engine
from shared.infrastructure.redis import close_redis, get_redis, init_redis


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    # Startup
    settings = get_settings()
    init_engine(settings.database_url)
    init_redis(settings.redis_url)
    yield  # noqa: RUF075
    # Shutdown
    await close_engine()
    await close_redis()


def create_app() -> FastAPI:
    settings = get_settings()

    # Configure structured logging
    # Default to INFO, but allow DEBUG if app_debug is True
    log_level = "DEBUG" if settings.app_debug else "INFO"
    setup_logging(log_level)

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        docs_url="/api/docs" if settings.app_debug else None,
        redoc_url="/api/redoc" if settings.app_debug else None,
        openapi_url="/api/openapi.json" if settings.app_debug else None,
        lifespan=lifespan,
    )

    # Setup middlewares
    app.add_middleware(RequestIDMiddleware)
    setup_cors(app, settings)

    # Register global domain exception to HTTP response handlers
    register_error_handlers(app)

    # Setup telemetry (OpenTelemetry tracers and instrumentation)
    setup_telemetry(app, settings)

    # Register module routers
    _register_routes(app)

    return app


def _register_routes(app: FastAPI) -> None:
    # 7. Health check endpoint returning status and connectivity states
    @app.get("/health", tags=["health"])
    async def health_check() -> dict[str, str]:
        db_status = "disconnected"
        redis_status = "disconnected"

        # Check Database
        try:
            session_factory = get_session_factory()
            async with session_factory() as session:
                await session.execute(text("SELECT 1"))
                db_status = "connected"
        except Exception:  # noqa: S110
            pass

        # Check Redis
        try:
            client = get_redis()
            await client.ping()
            redis_status = "connected"
        except Exception:  # noqa: S110
            pass

        overall_status = "healthy" if db_status == "connected" and redis_status == "connected" else "unhealthy"

        return {
            "status": overall_status,
            "database": db_status,
            "redis": redis_status,
        }

    # Readiness check (legacy or simple check)
    @app.get("/health/ready", tags=["health"])
    async def readiness_check() -> dict[str, str]:
        # Perform same database and redis checks
        res = await health_check()
        if res["status"] == "healthy":
            return {"status": "ready"}
        return {"status": "not_ready"}

    # Mount module routers under /api/v1/<module> prefix
    app.include_router(identity_router, prefix="/api/v1/auth", tags=["identity"])
    app.include_router(users_router, prefix="/api/v1/me", tags=["users"])
    app.include_router(restaurants_router, prefix="/api/v1/restaurants", tags=["restaurants"])
    app.include_router(menus_router, prefix="/api/v1/menus", tags=["menus"])
    app.include_router(orders_router, prefix="/api/v1/orders", tags=["orders"])
    app.include_router(payments_router, prefix="/api/v1/payments", tags=["payments"])
    app.include_router(deliveries_router, prefix="/api/v1/delivery-assignments", tags=["deliveries"])
    app.include_router(notifications_router, prefix="/api/v1/notifications", tags=["notifications"])
    app.include_router(reviews_router, prefix="/api/v1/reviews", tags=["reviews"])
    app.include_router(promotions_router, prefix="/api/v1/promotions", tags=["promotions"])
    app.include_router(analytics_router, prefix="/api/v1/admin/analytics", tags=["analytics"])
