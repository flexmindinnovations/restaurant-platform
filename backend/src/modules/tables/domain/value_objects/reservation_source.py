from enum import StrEnum


class ReservationSource(StrEnum):
    PLATFORM = "PLATFORM"
    PHONE = "PHONE"
    WALK_IN = "WALK_IN"
    THIRD_PARTY = "THIRD_PARTY"
