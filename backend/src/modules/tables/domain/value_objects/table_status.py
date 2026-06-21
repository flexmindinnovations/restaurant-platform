from enum import StrEnum


class TableStatus(StrEnum):
    AVAILABLE = "AVAILABLE"
    OCCUPIED = "OCCUPIED"
    RESERVED = "RESERVED"
    CLEANING = "CLEANING"
    BLOCKED = "BLOCKED"

    @property
    def is_assignable(self) -> bool:
        return self in {TableStatus.AVAILABLE, TableStatus.RESERVED}
