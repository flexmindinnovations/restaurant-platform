import re
from dataclasses import dataclass
from types import MappingProxyType

from shared.domain.exceptions import ValidationException
from shared.domain.value_objects import ValueObject

TIME_REGEX = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")


@dataclass(frozen=True)
class OperatingHours(ValueObject):
    schedule: dict[str, dict[str, str]]

    def __post_init__(self) -> None:
        valid_days = {"monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"}
        if not self.schedule:
            raise ValidationException("Schedule cannot be empty")
        for day, times in self.schedule.items():
            if day.lower() not in valid_days:
                raise ValidationException(f"Invalid day in schedule: {day}")
            if "open" not in times or "close" not in times:
                raise ValidationException(f"Missing 'open' or 'close' time for day: {day}")

            open_time = times["open"]
            close_time = times["close"]

            if not TIME_REGEX.match(open_time) or not TIME_REGEX.match(close_time):
                raise ValidationException(f"Invalid time format (must be HH:MM) for day: {day}")

        frozen = {day: MappingProxyType(times) for day, times in self.schedule.items()}
        object.__setattr__(self, "schedule", frozen)
