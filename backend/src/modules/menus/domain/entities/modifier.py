import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum

from shared.domain.entity import AggregateRoot, Entity
from shared.domain.exceptions import ValidationException
from shared.domain.value_objects import Money


class SelectionType(StrEnum):
    SINGLE = "SINGLE"
    MULTIPLE = "MULTIPLE"


@dataclass
class Modifier(Entity):
    modifier_group_id: uuid.UUID = None  # type: ignore[assignment]
    name: str = ""
    price_adjustment: Money = None  # type: ignore[assignment]
    is_default: bool = False
    is_available: bool = True
    display_order: int = 0


@dataclass
class ModifierGroup(AggregateRoot):
    menu_item_id: uuid.UUID = None  # type: ignore[assignment]
    restaurant_id: uuid.UUID = None  # type: ignore[assignment]
    name: str = ""
    description: str | None = None
    selection_type: SelectionType = SelectionType.SINGLE
    min_selections: int = 0
    max_selections: int = 1
    is_required: bool = False
    display_order: int = 0
    modifiers: list[Modifier] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        menu_item_id: uuid.UUID,
        restaurant_id: uuid.UUID,
        name: str,
        selection_type: SelectionType = SelectionType.SINGLE,
        min_selections: int = 0,
        max_selections: int = 1,
        is_required: bool = False,
        description: str | None = None,
        display_order: int = 0,
    ) -> "ModifierGroup":
        if not name:
            raise ValidationException("Modifier group name cannot be empty")
        if min_selections < 0:
            raise ValidationException("min_selections cannot be negative")
        if max_selections < 1:
            raise ValidationException("max_selections must be at least 1")
        if min_selections > max_selections:
            raise ValidationException("min_selections cannot exceed max_selections")

        now = datetime.now(UTC)
        return cls(
            id=uuid.uuid4(),
            menu_item_id=menu_item_id,
            restaurant_id=restaurant_id,
            name=name,
            description=description,
            selection_type=selection_type,
            min_selections=min_selections,
            max_selections=max_selections,
            is_required=is_required,
            display_order=display_order,
            modifiers=[],
            created_at=now,
            updated_at=now,
        )

    def add_modifier(
        self,
        name: str,
        price_adjustment: Money,
        is_default: bool = False,
        display_order: int = 0,
    ) -> Modifier:
        if not name:
            raise ValidationException("Modifier name cannot be empty")
        if price_adjustment.amount < 0:
            raise ValidationException("Price adjustment cannot be negative")

        now = datetime.now(UTC)
        modifier = Modifier(
            id=uuid.uuid4(),
            modifier_group_id=self.id,
            name=name,
            price_adjustment=price_adjustment,
            is_default=is_default,
            is_available=True,
            display_order=display_order,
            created_at=now,
            updated_at=now,
        )
        self.modifiers.append(modifier)
        self.updated_at = now
        return modifier

    def remove_modifier(self, modifier_id: uuid.UUID) -> None:
        self.modifiers = [m for m in self.modifiers if m.id != modifier_id]
        self.updated_at = datetime.now(UTC)

    def update_details(
        self,
        name: str | None = None,
        description: str | None = None,
        selection_type: SelectionType | None = None,
        min_selections: int | None = None,
        max_selections: int | None = None,
        is_required: bool | None = None,
        display_order: int | None = None,
    ) -> None:
        if name is not None:
            if not name:
                raise ValidationException("Modifier group name cannot be empty")
            self.name = name
        if description is not None:
            self.description = description
        if selection_type is not None:
            self.selection_type = selection_type

        new_min = min_selections if min_selections is not None else self.min_selections
        new_max = max_selections if max_selections is not None else self.max_selections
        if new_min > new_max:
            raise ValidationException("min_selections cannot exceed max_selections")
        self.min_selections = new_min
        self.max_selections = new_max

        if is_required is not None:
            self.is_required = is_required
        if display_order is not None:
            self.display_order = display_order
        self.updated_at = datetime.now(UTC)

    def validate_selection(self, selected_modifier_ids: list[uuid.UUID]) -> None:
        valid_ids = {m.id for m in self.modifiers if m.is_available}
        for sid in selected_modifier_ids:
            if sid not in valid_ids:
                raise ValidationException(f"Modifier {sid} is not available in group {self.name}")

        count = len(selected_modifier_ids)
        if self.is_required and count < self.min_selections:
            raise ValidationException(f"Group '{self.name}' requires at least {self.min_selections} selection(s)")
        if count > self.max_selections:
            raise ValidationException(f"Group '{self.name}' allows at most {self.max_selections} selection(s)")
