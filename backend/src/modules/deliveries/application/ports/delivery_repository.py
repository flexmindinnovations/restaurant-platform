import uuid
from abc import ABC, abstractmethod

from modules.deliveries.domain.entities.delivery import Delivery


class DeliveryRepository(ABC):
    @abstractmethod
    async def add(self, delivery: Delivery) -> None:
        pass

    @abstractmethod
    async def update(self, delivery: Delivery) -> None:
        pass

    @abstractmethod
    async def get_by_id(self, delivery_id: uuid.UUID) -> Delivery | None:
        pass

    @abstractmethod
    async def get_by_order_id(self, order_id: uuid.UUID) -> Delivery | None:
        pass

    @abstractmethod
    async def get_active_by_partner_id(self, partner_id: uuid.UUID) -> Delivery | None:
        pass

    @abstractmethod
    async def list_by_partner_id(self, partner_id: uuid.UUID) -> list[Delivery]:
        pass
