import re
from collections.abc import Callable
from dataclasses import dataclass

from shared.domain.exceptions import ValidationException
from shared.domain.value_objects import ValueObject

# Password complexity regex: min 8 chars, 1 uppercase, 1 lowercase, 1 digit, 1 special char
PASSWORD_REGEX = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
)


@dataclass(frozen=True)
class Password(ValueObject):
    hashed_value: str

    @classmethod
    def create(cls, plaintext: str, hash_fn: Callable[[str], str]) -> "Password":
        if not plaintext:
            raise ValidationException("Password cannot be empty")
        if not PASSWORD_REGEX.match(plaintext):
            raise ValidationException(
                "Password must be at least 8 characters long, and contain at least "
                "one uppercase letter, one lowercase letter, one number, and one special character."
            )
        return cls(hashed_value=hash_fn(plaintext))

    @classmethod
    def from_hash(cls, hashed_value: str) -> "Password":
        if not hashed_value:
            raise ValidationException("Hashed password cannot be empty")
        return cls(hashed_value=hashed_value)
