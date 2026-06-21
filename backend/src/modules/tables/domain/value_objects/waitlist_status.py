from enum import StrEnum


class WaitlistStatus(StrEnum):
    WAITING = "WAITING"
    NOTIFIED = "NOTIFIED"
    SEATED = "SEATED"
    LEFT = "LEFT"
    CANCELLED = "CANCELLED"

    @property
    def is_terminal(self) -> bool:
        return self in {WaitlistStatus.SEATED, WaitlistStatus.LEFT, WaitlistStatus.CANCELLED}
