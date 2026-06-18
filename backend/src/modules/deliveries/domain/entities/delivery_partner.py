import uuid
from dataclasses import dataclass
from decimal import Decimal

from modules.deliveries.domain.value_objects.location import GeoLocation
from modules.deliveries.domain.value_objects.vehicle_type import VehicleType
from shared.domain.entity import AggregateRoot


@dataclass
class DeliveryPartner(AggregateRoot):
    account_id: uuid.UUID = None  # type: ignore[assignment]
    name: str = ""
    phone: str = ""
    vehicle_type: VehicleType = VehicleType.MOTORCYCLE
    is_online: bool = False
    is_available: bool = True
    current_location: GeoLocation | None = None
    rating_avg: Decimal = Decimal("5.0")
    total_deliveries: int = 0

    @classmethod
    def register(
        cls,
        account_id: uuid.UUID,
        name: str,
        phone: str,
        vehicle_type: VehicleType = VehicleType.MOTORCYCLE,
    ) -> "DeliveryPartner":
        return cls(
            id=uuid.uuid4(),
            account_id=account_id,
            name=name,
            phone=phone,
            vehicle_type=vehicle_type,
            is_online=False,
            is_available=True,
            current_location=None,
            rating_avg=Decimal("5.0"),
            total_deliveries=0,
        )

    def toggle_online(self, is_online: bool) -> None:
        self.is_online = is_online

    def toggle_availability(self, is_available: bool) -> None:
        self.is_available = is_available

    def update_location(self, location: GeoLocation) -> None:
        self.current_location = location
