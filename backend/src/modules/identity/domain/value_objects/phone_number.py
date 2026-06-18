import re
from dataclasses import dataclass

from shared.domain.exceptions import ValidationException
from shared.domain.value_objects import ValueObject

# E.164 phone format: starting with +, then 1 to 15 digits
PHONE_REGEX = re.compile(r"^\+[1-9]\d{5,14}$")


@dataclass(frozen=True)
class PhoneNumber(ValueObject):
    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValidationException("Phone number cannot be empty")
        # Remove spaces or hyphens if any before validating
        normalized = self.value.strip().replace(" ", "").replace("-", "")
        if not PHONE_REGEX.match(normalized):
            raise ValidationException("Invalid phone number format. Must be E.164 compliant (e.g., +1234567890)")
        object.__setattr__(self, "value", normalized)
