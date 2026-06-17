from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    # Startup
    # TODO: Initialize database connection pool
    # TODO: Initialize Redis connection pool
    # TODO: Initialize OpenTelemetry
    yield
    # Shutdown
    # TODO: Close database connection pool
    # TODO: Close Redis connection pool


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        docs_url="/api/docs" if settings.app_debug else None,
        redoc_url="/api/redoc" if settings.app_debug else None,
        openapi_url="/api/openapi.json" if settings.app_debug else None,
        lifespan=lifespan,
    )

    _setup_middleware(app, settings)
    _register_routes(app)

    return app


def _setup_middleware(app: FastAPI, settings: object) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:4200"] if getattr(settings, "app_debug", False) else [],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def _register_routes(app: FastAPI) -> None:
    @app.get("/health", tags=["health"])
    async def health_check() -> dict[str, str]:
        return {"status": "healthy"}

    @app.get("/health/ready", tags=["health"])
    async def readiness_check() -> dict[str, str]:
        # TODO: Check database and Redis connectivity
        return {"status": "ready"}

    # TODO: Register module routers
    # app.include_router(identity_router, prefix="/api/v1/auth", tags=["identity"])
    # app.include_router(users_router, prefix="/api/v1/me", tags=["users"])
    # app.include_router(restaurants_router, prefix="/api/v1/restaurants", tags=["restaurants"])
    # app.include_router(menus_router, prefix="/api/v1/menus", tags=["menus"])
    # app.include_router(orders_router, prefix="/api/v1/orders", tags=["orders"])
    # app.include_router(payments_router, prefix="/api/v1/payments", tags=["payments"])
    # app.include_router(deliveries_router, prefix="/api/v1/delivery-assignments", tags=["deliveries"])
    # app.include_router(notifications_router, prefix="/api/v1/notifications", tags=["notifications"])
    # app.include_router(reviews_router, prefix="/api/v1/reviews", tags=["reviews"])
    # app.include_router(promotions_router, prefix="/api/v1/promotions", tags=["promotions"])
    # app.include_router(analytics_router, prefix="/api/v1/admin/analytics", tags=["analytics"])
