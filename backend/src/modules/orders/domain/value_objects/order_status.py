from enum import StrEnum


class OrderStatus(StrEnum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    PREPARING = "PREPARING"
    READY = "READY"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED = "DELIVERED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

    @property
    def is_terminal(self) -> bool:
        return self in {OrderStatus.COMPLETED, OrderStatus.CANCELLED}

    @property
    def is_cancellable(self) -> bool:
        return self in {OrderStatus.PENDING, OrderStatus.CONFIRMED}
