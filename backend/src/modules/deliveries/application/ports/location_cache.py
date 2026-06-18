import uuid
from abc import ABC, abstractmethod

from modules.deliveries.domain.value_objects.location import GeoLocation


class LocationCache(ABC):
    @abstractmethod
    async def update_location(self, partner_id: uuid.UUID, location: GeoLocation) -> None:
        pass

    @abstractmethod
    async def get_location(self, partner_id: uuid.UUID) -> GeoLocation | None:
        pass

    @abstractmethod
    async def publish_tracking_update(self, order_id: uuid.UUID, data: dict) -> None:
        pass
