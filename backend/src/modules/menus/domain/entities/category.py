import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from shared.domain.entity import Entity
from shared.domain.exceptions import ValidationException


@dataclass
class Category(Entity):
    menu_id: uuid.UUID = None  # type: ignore[assignment]
    name: str = ""
    description: str | None = None
    display_order: int = 0
    is_active: bool = True

    @classmethod
    def create(
        cls,
        menu_id: uuid.UUID,
        name: str,
        description: str | None = None,
        display_order: int = 0,
    ) -> "Category":
        if not name:
            raise ValidationException("Category name cannot be empty")

        return cls(
            id=uuid.uuid4(),
            menu_id=menu_id,
            name=name,
            description=description,
            display_order=display_order,
            is_active=True,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

    def update(
        self,
        name: str | None = None,
        description: str | None = None,
        display_order: int | None = None,
    ) -> None:
        if name is not None:
            if not name:
                raise ValidationException("Category name cannot be empty")
            self.name = name
        if description is not None:
            self.description = description
        if display_order is not None:
            self.display_order = display_order
        self.updated_at = datetime.now(UTC)

    def deactivate(self) -> None:
        self.is_active = False
        self.updated_at = datetime.now(UTC)
