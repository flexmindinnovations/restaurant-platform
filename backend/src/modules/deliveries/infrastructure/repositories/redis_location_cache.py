import json
import uuid
from decimal import Decimal

from redis.asyncio import Redis

from modules.deliveries.application.ports.location_cache import LocationCache
from modules.deliveries.domain.value_objects.location import GeoLocation


class RedisLocationCache(LocationCache):
    def __init__(self, redis_client: Redis) -> None:
        self._redis = redis_client

    async def update_location(self, partner_id: uuid.UUID, location: GeoLocation) -> None:
        key = "delivery_partners:locations"
        # Redis GEOADD expects: key, (longitude, latitude, member)
        await self._redis.geoadd(
            key,
            (float(location.longitude), float(location.latitude), str(partner_id))
        )

    async def get_location(self, partner_id: uuid.UUID) -> GeoLocation | None:
        key = "delivery_partners:locations"
        # GEOPOS returns list of (longitude, latitude) tuples
        pos = await self._redis.geopos(key, str(partner_id))
        if pos and pos[0]:
            lon, lat = pos[0]
            return GeoLocation(latitude=Decimal(str(lat)), longitude=Decimal(str(lon)))
        return None

    async def publish_tracking_update(self, order_id: uuid.UUID, data: dict) -> None:
        # Publish order tracking updates to the Redis pub/sub channel
        channel = f"order:{order_id}:tracking"
        await self._redis.publish(channel, json.dumps(data))
