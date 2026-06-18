import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from modules.menus.domain.events.menu_events import (
    MenuCreated,
    MenuPublished,
    MenuUnpublished,
    MenuUpdated,
)
from shared.domain.entity import AggregateRoot
from shared.domain.exceptions import ValidationException


@dataclass
class Menu(AggregateRoot):
    restaurant_id: uuid.UUID = None  # type: ignore[assignment]
    name: str = ""
    description: str | None = None
    is_active: bool = False

    @classmethod
    def create(
        cls,
        restaurant_id: uuid.UUID,
        name: str,
        description: str | None = None,
    ) -> "Menu":
        if not name:
            raise ValidationException("Menu name cannot be empty")

        menu_id = uuid.uuid4()
        menu = cls(
            id=menu_id,
            restaurant_id=restaurant_id,
            name=name,
            description=description,
            is_active=False,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        menu.register_event(
            MenuCreated(
                aggregate_id=menu_id,
                restaurant_id=restaurant_id,
                name=name,
            )
        )
        return menu

    def update_details(
        self,
        name: str | None = None,
        description: str | None = None,
    ) -> None:
        if name is not None:
            if not name:
                raise ValidationException("Menu name cannot be empty")
            self.name = name
        if description is not None:
            self.description = description
        self.updated_at = datetime.now(UTC)
        self.register_event(MenuUpdated(aggregate_id=self.id))

    def publish(self) -> None:
        if self.is_active:
            return
        self.is_active = True
        self.updated_at = datetime.now(UTC)
        self.register_event(MenuPublished(aggregate_id=self.id))

    def unpublish(self) -> None:
        if not self.is_active:
            return
        self.is_active = False
        self.updated_at = datetime.now(UTC)
        self.register_event(MenuUnpublished(aggregate_id=self.id))
