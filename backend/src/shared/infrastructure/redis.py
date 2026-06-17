from redis.asyncio import ConnectionPool, Redis

_pool: ConnectionPool | None = None


def init_redis(redis_url: str) -> ConnectionPool:
    global _pool
    _pool = ConnectionPool.from_url(redis_url, decode_responses=True)
    return _pool


def get_redis() -> Redis:
    if _pool is None:
        raise RuntimeError("Redis pool not initialized. Call init_redis() first.")
    return Redis(connection_pool=_pool)


async def close_redis() -> None:
    global _pool
    if _pool is not None:
        await _pool.disconnect()
        _pool = None
