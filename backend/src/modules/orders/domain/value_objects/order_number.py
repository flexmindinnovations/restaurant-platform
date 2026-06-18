import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from shared.domain.value_objects import ValueObject


@dataclass(frozen=True)
class OrderNumber(ValueObject):
    value: str

    @classmethod
    def generate(cls) -> "OrderNumber":
        date_str = datetime.now(UTC).strftime("%Y%m%d")
        hex_str = uuid.uuid4().hex[:4].upper()
        return cls(f"ORD-{date_str}-{hex_str}")
