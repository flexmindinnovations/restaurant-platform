import uuid
from abc import ABC, abstractmethod
from decimal import Decimal

from modules.deliveries.domain.entities.delivery_partner import DeliveryPartner
from modules.deliveries.domain.value_objects.location import GeoLocation


class PartnerRepository(ABC):
    @abstractmethod
    async def add(self, partner: DeliveryPartner) -> None:
        pass

    @abstractmethod
    async def update(self, partner: DeliveryPartner) -> None:
        pass

    @abstractmethod
    async def get_by_id(self, partner_id: uuid.UUID) -> DeliveryPartner | None:
        pass

    @abstractmethod
    async def get_by_account_id(self, account_id: uuid.UUID) -> DeliveryPartner | None:
        pass

    @abstractmethod
    async def find_nearest_available(
        self, location: GeoLocation, radius_km: Decimal, limit: int = 5
    ) -> list[DeliveryPartner]:
        pass
