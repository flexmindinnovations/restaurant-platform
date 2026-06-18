import uuid
from dataclasses import dataclass
from decimal import Decimal

from shared.domain.events import DomainEvent


@dataclass(frozen=True, kw_only=True)
class DeliveryCreated(DomainEvent):
    delivery_id: uuid.UUID
    order_id: uuid.UUID
    restaurant_id: uuid.UUID


@dataclass(frozen=True, kw_only=True)
class PartnerAssigned(DomainEvent):
    delivery_id: uuid.UUID
    partner_id: uuid.UUID


@dataclass(frozen=True, kw_only=True)
class PickupCompleted(DomainEvent):
    delivery_id: uuid.UUID


@dataclass(frozen=True, kw_only=True)
class DeliveryCompleted(DomainEvent):
    delivery_id: uuid.UUID
    order_id: uuid.UUID


@dataclass(frozen=True, kw_only=True)
class LocationUpdated(DomainEvent):
    delivery_id: uuid.UUID
    latitude: Decimal
    longitude: Decimal
