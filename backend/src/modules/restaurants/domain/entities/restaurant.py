import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime

from modules.restaurants.domain.events.restaurant_events import (
    RestaurantDeactivated,
    RestaurantRegistered,
    RestaurantVerified,
)
from shared.domain.value_objects import Address
from modules.restaurants.domain.value_objects.operating_hours import OperatingHours
from shared.domain.entity import AggregateRoot
from shared.domain.exceptions import ValidationException


@dataclass
class Restaurant(AggregateRoot):
    owner_id: uuid.UUID = None  # type: ignore[assignment]
    name: str = ""
    address: Address = None  # type: ignore[assignment]
    phone: str = ""
    email: str = ""
    operating_hours: OperatingHours = None  # type: ignore[assignment]
    description: str | None = None
    cuisine_types: list[str] = field(default_factory=list)
    is_active: bool = True
    is_verified: bool = False
    rating_avg: float = 0.0
    total_reviews: int = 0

    @classmethod
    def register(
        cls,
        owner_id: uuid.UUID,
        name: str,
        address: Address,
        phone: str,
        email: str,
        operating_hours: OperatingHours,
        description: str | None = None,
        cuisine_types: list[str] | None = None,
    ) -> "Restaurant":
        if not name:
            raise ValidationException("Restaurant name cannot be empty")
        if not phone:
            raise ValidationException("Restaurant phone cannot be empty")
        if not email:
            raise ValidationException("Restaurant email cannot be empty")

        restaurant_id = uuid.uuid4()
        cuisines = cuisine_types or []

        restaurant = cls(
            id=restaurant_id,
            owner_id=owner_id,
            name=name,
            address=address,
            phone=phone,
            email=email,
            operating_hours=operating_hours,
            description=description,
            cuisine_types=cuisines,
            is_active=True,
            is_verified=False,
            rating_avg=0.0,
            total_reviews=0,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        restaurant.register_event(
            RestaurantRegistered(
                aggregate_id=restaurant_id,
                owner_id=owner_id,
                name=name,
            )
        )
        return restaurant

    def update_details(
        self,
        name: str | None = None,
        description: str | None = None,
        cuisine_types: list[str] | None = None,
        address: Address | None = None,
        phone: str | None = None,
        email: str | None = None,
        operating_hours: OperatingHours | None = None,
    ) -> None:
        if not self.is_active:
            raise ValidationException("Cannot update inactive restaurant")

        if name is not None:
            if not name:
                raise ValidationException("Restaurant name cannot be empty")
            self.name = name
        if description is not None:
            self.description = description
        if cuisine_types is not None:
            self.cuisine_types = cuisine_types
        if address is not None:
            self.address = address
        if phone is not None:
            if not phone:
                raise ValidationException("Phone number cannot be empty")
            self.phone = phone
        if email is not None:
            if not email:
                raise ValidationException("Email address cannot be empty")
            self.email = email
        if operating_hours is not None:
            self.operating_hours = operating_hours

        self.updated_at = datetime.now(UTC)

    def verify(self) -> None:
        if not self.is_active:
            raise ValidationException("Cannot verify inactive restaurant")
        if self.is_verified:
            return  # Idempotent

        self.is_verified = True
        self.updated_at = datetime.now(UTC)
        self.register_event(RestaurantVerified(aggregate_id=self.id))

    def deactivate(self) -> None:
        if not self.is_active:
            return

        self.is_active = False
        self.updated_at = datetime.now(UTC)
        self.register_event(RestaurantDeactivated(aggregate_id=self.id))
