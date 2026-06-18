import uuid
from dataclasses import dataclass

from modules.deliveries.application.ports.delivery_repository import DeliveryRepository
from modules.deliveries.application.ports.location_cache import LocationCache
from modules.deliveries.domain.value_objects.location import GeoLocation


@dataclass(frozen=True)
class UpdatePartnerLocationCommand:
    partner_id: uuid.UUID
    location: GeoLocation


class UpdatePartnerLocationHandler:
    def __init__(
        self,
        delivery_repo: DeliveryRepository,
        location_cache: LocationCache,
    ) -> None:
        self._delivery_repo = delivery_repo
        self._location_cache = location_cache

    async def handle(self, command: UpdatePartnerLocationCommand) -> None:
        # 1. Update location in the Redis Geospatial Cache
        await self._location_cache.update_location(command.partner_id, command.location)

        # 2. Retrieve active delivery (if any) to broadcast update
        delivery = await self._delivery_repo.get_active_by_partner_id(command.partner_id)
        if delivery:
            # Broadcast the coordinate update to the order tracking channel
            await self._location_cache.publish_tracking_update(
                order_id=delivery.order_id,
                data={
                    "order_id": str(delivery.order_id),
                    "delivery_id": str(delivery.id),
                    "latitude": float(command.location.latitude),
                    "longitude": float(command.location.longitude),
                    "status": delivery.status,
                }
            )
