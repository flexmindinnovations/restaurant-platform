import pytest
from httpx import ASGITransport, AsyncClient
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings
from app.main import create_app


@pytest.fixture
async def app():
    """Fixture to create the FastAPI application instance."""
    app_instance = create_app()
    async with app_instance.router.lifespan_context(app_instance):
        yield app_instance


@pytest.fixture
async def client(app) -> AsyncClient:
    """Fixture to create an HTTPX async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def db_session() -> AsyncSession:
    """Fixture to create an isolated SQLAlchemy database session for tests."""
    settings = get_settings()
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
    await engine.dispose()


@pytest.fixture
async def redis_client() -> Redis:
    """Fixture to create a Redis client for tests."""
    settings = get_settings()
    client = Redis.from_url(settings.redis_url, decode_responses=True)
    yield client
    await client.close()
