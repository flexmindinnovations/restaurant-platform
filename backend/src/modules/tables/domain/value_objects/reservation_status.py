from enum import StrEnum


class ReservationStatus(StrEnum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    SEATED = "SEATED"
    COMPLETED = "COMPLETED"
    NO_SHOW = "NO_SHOW"
    CANCELLED = "CANCELLED"

    @property
    def is_terminal(self) -> bool:
        return self in {ReservationStatus.COMPLETED, ReservationStatus.NO_SHOW, ReservationStatus.CANCELLED}

    @property
    def is_cancellable(self) -> bool:
        return self in {ReservationStatus.PENDING, ReservationStatus.CONFIRMED}
