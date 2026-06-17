import re
from dataclasses import dataclass

from shared.domain.exceptions import ValidationException
from shared.domain.value_objects import ValueObject

# Simple email validation regex
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


@dataclass(frozen=True)
class Email(ValueObject):
    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValidationException("Email cannot be empty")
        normalized = self.value.strip().lower()
        if not EMAIL_REGEX.match(normalized):
            raise ValidationException("Invalid email format")
        object.__setattr__(self, "value", normalized)
