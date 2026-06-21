import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from modules.tables.domain.events.table_events import TableStatusChanged
from modules.tables.domain.value_objects.table_shape import TableShape
from modules.tables.domain.value_objects.table_status import TableStatus
from shared.domain.entity import AggregateRoot
from shared.domain.exceptions import ValidationException


@dataclass
class Table(AggregateRoot):
    restaurant_id: uuid.UUID = None  # type: ignore[assignment]
    section_id: uuid.UUID | None = None
    number: str = ""
    capacity_min: int = 1
    capacity_max: int = 1
    shape: TableShape = TableShape.RECTANGULAR
    position_x: int = 0
    position_y: int = 0
    status: TableStatus = TableStatus.AVAILABLE
    turn_time_minutes: int = 90
    buffer_minutes: int = 15
    is_active: bool = True

    @classmethod
    def create(
        cls,
        restaurant_id: uuid.UUID,
        number: str,
        capacity_min: int,
        capacity_max: int,
        shape: TableShape = TableShape.RECTANGULAR,
        section_id: uuid.UUID | None = None,
        position_x: int = 0,
        position_y: int = 0,
        turn_time_minutes: int = 90,
        buffer_minutes: int = 15,
    ) -> "Table":
        if not number:
            raise ValidationException("Table number cannot be empty")
        if len(number) > 20:
            raise ValidationException("Table number must not exceed 20 characters")
        if capacity_min < 1:
            raise ValidationException("Minimum capacity must be at least 1")
        if capacity_max < capacity_min:
            raise ValidationException("Maximum capacity must be greater than or equal to minimum capacity")

        now = datetime.now(UTC)
        return cls(
            id=uuid.uuid4(),
            restaurant_id=restaurant_id,
            section_id=section_id,
            number=number,
            capacity_min=capacity_min,
            capacity_max=capacity_max,
            shape=shape,
            position_x=position_x,
            position_y=position_y,
            status=TableStatus.AVAILABLE,
            turn_time_minutes=turn_time_minutes,
            buffer_minutes=buffer_minutes,
            is_active=True,
            created_at=now,
            updated_at=now,
        )

    def change_status(self, new_status: TableStatus, changed_by: uuid.UUID | None = None) -> None:
        if self.status == new_status:
            return
        old_status = self.status
        self.status = new_status
        self.updated_at = datetime.now(UTC)
        self.register_event(
            TableStatusChanged(
                aggregate_id=self.id,
                table_id=self.id,
                restaurant_id=self.restaurant_id,
                old_status=old_status,
                new_status=new_status,
                changed_by=changed_by,
            )
        )

    def update_details(
        self,
        number: str | None = None,
        capacity_min: int | None = None,
        capacity_max: int | None = None,
        shape: TableShape | None = None,
        section_id: uuid.UUID | None = None,
        position_x: int | None = None,
        position_y: int | None = None,
        turn_time_minutes: int | None = None,
        buffer_minutes: int | None = None,
    ) -> None:
        if number is not None:
            if not number:
                raise ValidationException("Table number cannot be empty")
            if len(number) > 20:
                raise ValidationException("Table number must not exceed 20 characters")
            self.number = number
        if capacity_min is not None:
            if capacity_min < 1:
                raise ValidationException("Minimum capacity must be at least 1")
            self.capacity_min = capacity_min
        if capacity_max is not None:
            self.capacity_max = capacity_max
        if self.capacity_max < self.capacity_min:
            raise ValidationException("Maximum capacity must be greater than or equal to minimum capacity")
        if shape is not None:
            self.shape = shape
        if section_id is not None:
            self.section_id = section_id
        if position_x is not None:
            self.position_x = position_x
        if position_y is not None:
            self.position_y = position_y
        if turn_time_minutes is not None:
            self.turn_time_minutes = turn_time_minutes
        if buffer_minutes is not None:
            self.buffer_minutes = buffer_minutes
        self.updated_at = datetime.now(UTC)

    def deactivate(self) -> None:
        self.is_active = False
        self.updated_at = datetime.now(UTC)

    def activate(self) -> None:
        self.is_active = True
        self.updated_at = datetime.now(UTC)

    def can_seat(self, party_size: int) -> bool:
        return (
            self.is_active
            and self.status == TableStatus.AVAILABLE
            and self.capacity_min <= party_size <= self.capacity_max
        )
