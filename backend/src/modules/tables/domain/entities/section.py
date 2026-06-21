import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from shared.domain.entity import AggregateRoot
from shared.domain.exceptions import ValidationException


@dataclass
class Section(AggregateRoot):
    restaurant_id: uuid.UUID = None  # type: ignore[assignment]
    name: str = ""
    description: str | None = None
    display_order: int = 0
    is_active: bool = True

    @classmethod
    def create(
        cls,
        restaurant_id: uuid.UUID,
        name: str,
        description: str | None = None,
        display_order: int = 0,
    ) -> "Section":
        if not name:
            raise ValidationException("Section name cannot be empty")
        if len(name) > 100:
            raise ValidationException("Section name must not exceed 100 characters")

        now = datetime.now(UTC)
        return cls(
            id=uuid.uuid4(),
            restaurant_id=restaurant_id,
            name=name,
            description=description,
            display_order=display_order,
            is_active=True,
            created_at=now,
            updated_at=now,
        )

    def update_details(
        self,
        name: str | None = None,
        description: str | None = None,
        display_order: int | None = None,
    ) -> None:
        if name is not None:
            if not name:
                raise ValidationException("Section name cannot be empty")
            if len(name) > 100:
                raise ValidationException("Section name must not exceed 100 characters")
            self.name = name
        if description is not None:
            self.description = description
        if display_order is not None:
            self.display_order = display_order
        self.updated_at = datetime.now(UTC)

    def deactivate(self) -> None:
        self.is_active = False
        self.updated_at = datetime.now(UTC)

    def activate(self) -> None:
        self.is_active = True
        self.updated_at = datetime.now(UTC)
