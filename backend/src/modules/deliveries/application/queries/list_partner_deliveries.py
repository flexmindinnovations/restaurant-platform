import uuid
from dataclasses import dataclass

from modules.deliveries.application.ports.delivery_repository import DeliveryRepository
from modules.deliveries.application.queries.get_delivery import DeliveryDTO


@dataclass(frozen=True)
class ListPartnerDeliveriesQuery:
    partner_id: uuid.UUID


class ListPartnerDeliveriesHandler:
    def __init__(self, delivery_repo: DeliveryRepository) -> None:
        self._delivery_repo = delivery_repo

    async def handle(self, query: ListPartnerDeliveriesQuery) -> list[DeliveryDTO]:
        deliveries = await self._delivery_repo.list_by_partner_id(query.partner_id)
        return [DeliveryDTO.from_entity(d) for d in deliveries]
