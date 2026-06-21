from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime

from modules.tables.application.ports.section_repository import SectionRepository
from modules.tables.application.ports.table_repository import TableRepository


@dataclass(frozen=True)
class TableDTO:
    id: uuid.UUID
    restaurant_id: uuid.UUID
    section_id: uuid.UUID | None
    number: str
    capacity_min: int
    capacity_max: int
    shape: str
    position_x: int
    position_y: int
    status: str
    turn_time_minutes: int
    buffer_minutes: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class SectionDTO:
    id: uuid.UUID
    restaurant_id: uuid.UUID
    name: str
    description: str | None
    display_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    tables: list[TableDTO] = field(default_factory=list)


@dataclass(frozen=True)
class FloorPlanDTO:
    sections: list[SectionDTO]
    unassigned_tables: list[TableDTO]


@dataclass(frozen=True)
class GetFloorPlanQuery:
    restaurant_id: uuid.UUID


class GetFloorPlanHandler:
    def __init__(self, section_repo: SectionRepository, table_repo: TableRepository) -> None:
        self._section_repo = section_repo
        self._table_repo = table_repo

    async def handle(self, query: GetFloorPlanQuery) -> FloorPlanDTO:
        sections = await self._section_repo.list_by_restaurant(query.restaurant_id)
        tables = await self._table_repo.list_by_restaurant(query.restaurant_id)

        tables_by_section: dict[uuid.UUID | None, list[TableDTO]] = {}
        for t in tables:
            dto = TableDTO(
                id=t.id,
                restaurant_id=t.restaurant_id,
                section_id=t.section_id,
                number=t.number,
                capacity_min=t.capacity_min,
                capacity_max=t.capacity_max,
                shape=t.shape.value,
                position_x=t.position_x,
                position_y=t.position_y,
                status=t.status.value,
                turn_time_minutes=t.turn_time_minutes,
                buffer_minutes=t.buffer_minutes,
                is_active=t.is_active,
                created_at=t.created_at,
                updated_at=t.updated_at,
            )
            tables_by_section.setdefault(t.section_id, []).append(dto)

        section_dtos = [
            SectionDTO(
                id=s.id,
                restaurant_id=s.restaurant_id,
                name=s.name,
                description=s.description,
                display_order=s.display_order,
                is_active=s.is_active,
                created_at=s.created_at,
                updated_at=s.updated_at,
                tables=tables_by_section.get(s.id, []),
            )
            for s in sorted(sections, key=lambda s: s.display_order)
        ]

        return FloorPlanDTO(
            sections=section_dtos,
            unassigned_tables=tables_by_section.get(None, []),
        )
