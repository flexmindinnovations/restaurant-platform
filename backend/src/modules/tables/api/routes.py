import uuid
from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, Query, status

from modules.tables.api.dependencies import (
    get_cancel_reservation_handler,
    get_confirm_reservation_handler,
    get_create_reservation_handler,
    get_create_section_handler,
    get_create_table_handler,
    get_delete_section_handler,
    get_delete_table_handler,
    get_join_waitlist_handler,
    get_mark_no_show_handler,
    get_notify_waitlist_handler,
    get_remove_from_waitlist_handler,
    get_seat_from_waitlist_handler,
    get_seat_reservation_handler,
    get_update_section_handler,
    get_update_table_handler,
    get_update_table_status_handler,
)
from modules.tables.api.schemas.table_schemas import (
    CancelReservationRequest,
    ConfirmReservationRequest,
    CreateReservationRequest,
    CreateSectionRequest,
    CreateTableRequest,
    JoinWaitlistRequest,
    ReservationListResponse,
    ReservationResponse,
    SectionListResponse,
    SectionResponse,
    TableListResponse,
    TableResponse,
    UpdateSectionRequest,
    UpdateTableRequest,
    UpdateTableStatusRequest,
    WaitlistEntryResponse,
    WaitlistListResponse,
)
from modules.tables.application.commands.cancel_reservation import CancelReservationCommand, CancelReservationHandler
from modules.tables.application.commands.confirm_reservation import (
    ConfirmReservationCommand,
    ConfirmReservationHandler,
)
from modules.tables.application.commands.create_reservation import CreateReservationCommand, CreateReservationHandler
from modules.tables.application.commands.create_section import CreateSectionCommand, CreateSectionHandler
from modules.tables.application.commands.create_table import CreateTableCommand, CreateTableHandler
from modules.tables.application.commands.delete_section import DeleteSectionCommand, DeleteSectionHandler
from modules.tables.application.commands.delete_table import DeleteTableCommand, DeleteTableHandler
from modules.tables.application.commands.join_waitlist import JoinWaitlistCommand, JoinWaitlistHandler
from modules.tables.application.commands.mark_no_show import MarkNoShowCommand, MarkNoShowHandler
from modules.tables.application.commands.notify_waitlist import NotifyWaitlistCommand, NotifyWaitlistHandler
from modules.tables.application.commands.remove_from_waitlist import (
    RemoveFromWaitlistCommand,
    RemoveFromWaitlistHandler,
)
from modules.tables.application.commands.seat_from_waitlist import SeatFromWaitlistCommand, SeatFromWaitlistHandler
from modules.tables.application.commands.seat_reservation import SeatReservationCommand, SeatReservationHandler
from modules.tables.application.commands.update_section import UpdateSectionCommand, UpdateSectionHandler
from modules.tables.application.commands.update_table import UpdateTableCommand, UpdateTableHandler
from modules.tables.application.commands.update_table_status import (
    UpdateTableStatusCommand,
    UpdateTableStatusHandler,
)
from modules.tables.domain.value_objects.reservation_source import ReservationSource
from modules.tables.domain.value_objects.table_shape import TableShape
from modules.tables.domain.value_objects.table_status import TableStatus
from shared.api.response import ResponseEnvelope
from shared.api.security import require_roles

router = APIRouter()


# ---------------------------------------------------------------------------
# Sections
# ---------------------------------------------------------------------------


@router.post("/sections", response_model=ResponseEnvelope[SectionResponse], status_code=status.HTTP_201_CREATED)
async def create_section(
    request: CreateSectionRequest,
    current_user: dict[str, Any] = Depends(require_roles("RESTAURANT_OWNER", "SUPER_ADMIN")),
    handler: CreateSectionHandler = Depends(get_create_section_handler),
) -> ResponseEnvelope[SectionResponse]:
    restaurant_id = uuid.UUID(current_user["restaurant_id"])
    command = CreateSectionCommand(
        restaurant_id=restaurant_id,
        name=request.name,
        description=request.description,
        display_order=request.display_order,
    )
    section_id = await handler.handle(command)
    return ResponseEnvelope(data=SectionResponse(
        id=section_id,
        restaurant_id=restaurant_id,
        name=request.name,
        description=request.description,
        display_order=request.display_order,
        is_active=True,
        created_at=command.created_at if hasattr(command, "created_at") else __import__("datetime").datetime.now(
            __import__("datetime").UTC
        ),
        updated_at=command.updated_at if hasattr(command, "updated_at") else __import__("datetime").datetime.now(
            __import__("datetime").UTC
        ),
    ))


@router.get("/sections", response_model=ResponseEnvelope[SectionListResponse])
async def list_sections(
    restaurant_id: uuid.UUID = Query(...),
    active_only: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    handler: CreateSectionHandler = Depends(get_create_section_handler),
) -> ResponseEnvelope[SectionListResponse]:
    from modules.tables.infrastructure.repositories.section_repository import SqlAlchemySectionRepository

    repo: SqlAlchemySectionRepository = handler._section_repo  # type: ignore[attr-defined]
    sections = await repo.list_by_restaurant(restaurant_id, active_only=active_only, skip=skip, limit=limit)
    items = [SectionResponse.model_validate(s) for s in sections]
    return ResponseEnvelope(data=SectionListResponse(items=items, total=len(items)))


@router.patch("/sections/{section_id}", response_model=ResponseEnvelope[dict])
async def update_section(
    section_id: uuid.UUID,
    request: UpdateSectionRequest,
    _current_user: dict[str, Any] = Depends(require_roles("RESTAURANT_OWNER", "SUPER_ADMIN")),
    handler: UpdateSectionHandler = Depends(get_update_section_handler),
) -> ResponseEnvelope[dict]:
    command = UpdateSectionCommand(
        section_id=section_id,
        name=request.name,
        description=request.description,
        display_order=request.display_order,
    )
    await handler.handle(command)
    return ResponseEnvelope(data={"message": "Section updated successfully"})


@router.delete("/sections/{section_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_section(
    section_id: uuid.UUID,
    _current_user: dict[str, Any] = Depends(require_roles("RESTAURANT_OWNER", "SUPER_ADMIN")),
    handler: DeleteSectionHandler = Depends(get_delete_section_handler),
) -> None:
    await handler.handle(DeleteSectionCommand(section_id=section_id))


# ---------------------------------------------------------------------------
# Tables
# ---------------------------------------------------------------------------


@router.post("", response_model=ResponseEnvelope[TableResponse], status_code=status.HTTP_201_CREATED)
async def create_table(
    request: CreateTableRequest,
    current_user: dict[str, Any] = Depends(require_roles("RESTAURANT_OWNER", "SUPER_ADMIN")),
    handler: CreateTableHandler = Depends(get_create_table_handler),
) -> ResponseEnvelope[TableResponse]:
    restaurant_id = uuid.UUID(current_user["restaurant_id"])
    command = CreateTableCommand(
        restaurant_id=restaurant_id,
        number=request.number,
        capacity_min=request.capacity_min,
        capacity_max=request.capacity_max,
        shape=TableShape(request.shape),
        section_id=request.section_id,
        position_x=request.position_x,
        position_y=request.position_y,
        turn_time_minutes=request.turn_time_minutes,
        buffer_minutes=request.buffer_minutes,
    )
    table_id = await handler.handle(command)
    from datetime import UTC, datetime

    now = datetime.now(UTC)
    return ResponseEnvelope(data=TableResponse(
        id=table_id,
        restaurant_id=restaurant_id,
        section_id=request.section_id,
        number=request.number,
        capacity_min=request.capacity_min,
        capacity_max=request.capacity_max,
        shape=request.shape,
        position_x=request.position_x,
        position_y=request.position_y,
        status=TableStatus.AVAILABLE.value,
        turn_time_minutes=request.turn_time_minutes,
        buffer_minutes=request.buffer_minutes,
        is_active=True,
        created_at=now,
        updated_at=now,
    ))


@router.get("", response_model=ResponseEnvelope[TableListResponse])
async def list_tables(
    restaurant_id: uuid.UUID = Query(...),
    section_id: uuid.UUID | None = Query(None),
    active_only: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    handler: CreateTableHandler = Depends(get_create_table_handler),
) -> ResponseEnvelope[TableListResponse]:
    repo = handler._table_repo  # type: ignore[attr-defined]
    tables = await repo.list_by_restaurant(
        restaurant_id, section_id=section_id, active_only=active_only, skip=skip, limit=limit
    )
    items = [TableResponse.model_validate(t) for t in tables]
    total = await repo.count_by_restaurant(restaurant_id, active_only=active_only)
    return ResponseEnvelope(data=TableListResponse(items=items, total=total))


@router.patch("/{table_id}", response_model=ResponseEnvelope[dict])
async def update_table(
    table_id: uuid.UUID,
    request: UpdateTableRequest,
    _current_user: dict[str, Any] = Depends(require_roles("RESTAURANT_OWNER", "SUPER_ADMIN")),
    handler: UpdateTableHandler = Depends(get_update_table_handler),
) -> ResponseEnvelope[dict]:
    command = UpdateTableCommand(
        table_id=table_id,
        number=request.number,
        capacity_min=request.capacity_min,
        capacity_max=request.capacity_max,
        shape=TableShape(request.shape) if request.shape else None,
        section_id=request.section_id,
        position_x=request.position_x,
        position_y=request.position_y,
        turn_time_minutes=request.turn_time_minutes,
        buffer_minutes=request.buffer_minutes,
    )
    await handler.handle(command)
    return ResponseEnvelope(data={"message": "Table updated successfully"})


@router.patch("/{table_id}/status", response_model=ResponseEnvelope[dict])
async def update_table_status(
    table_id: uuid.UUID,
    request: UpdateTableStatusRequest,
    _current_user: dict[str, Any] = Depends(require_roles("RESTAURANT_OWNER", "RESTAURANT_STAFF", "SUPER_ADMIN")),
    handler: UpdateTableStatusHandler = Depends(get_update_table_status_handler),
) -> ResponseEnvelope[dict]:
    command = UpdateTableStatusCommand(
        table_id=table_id,
        new_status=TableStatus(request.status),
    )
    await handler.handle(command)
    return ResponseEnvelope(data={"message": "Table status updated successfully"})


@router.delete("/{table_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_table(
    table_id: uuid.UUID,
    _current_user: dict[str, Any] = Depends(require_roles("RESTAURANT_OWNER", "SUPER_ADMIN")),
    handler: DeleteTableHandler = Depends(get_delete_table_handler),
) -> None:
    await handler.handle(DeleteTableCommand(table_id=table_id))


# ---------------------------------------------------------------------------
# Reservations
# ---------------------------------------------------------------------------


@router.post("/reservations", response_model=ResponseEnvelope[dict], status_code=status.HTTP_201_CREATED)
async def create_reservation(
    request: CreateReservationRequest,
    handler: CreateReservationHandler = Depends(get_create_reservation_handler),
) -> ResponseEnvelope[dict]:
    command = CreateReservationCommand(
        restaurant_id=request.restaurant_id,
        customer_name=request.customer_name,
        date=request.date,
        start_time=request.start_time,
        party_size=request.party_size,
        table_id=request.table_id,
        customer_phone=request.customer_phone,
        customer_email=request.customer_email,
        special_requests=request.special_requests,
        source=ReservationSource(request.source),
    )
    reservation_id = await handler.handle(command)
    return ResponseEnvelope(data={"id": str(reservation_id), "message": "Reservation created"})


@router.get("/reservations", response_model=ResponseEnvelope[ReservationListResponse])
async def list_reservations(
    restaurant_id: uuid.UUID = Query(...),
    reservation_date: date | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    handler: CreateReservationHandler = Depends(get_create_reservation_handler),
) -> ResponseEnvelope[ReservationListResponse]:
    repo = handler._reservation_repo  # type: ignore[attr-defined]
    reservations = await repo.list_by_restaurant(
        restaurant_id, reservation_date=reservation_date, skip=skip, limit=limit
    )
    total = await repo.count_by_restaurant(restaurant_id, reservation_date=reservation_date)
    items = [ReservationResponse.model_validate(r) for r in reservations]
    return ResponseEnvelope(data=ReservationListResponse(items=items, total=total))


@router.get("/reservations/{reservation_id}", response_model=ResponseEnvelope[ReservationResponse])
async def get_reservation(
    reservation_id: uuid.UUID,
    handler: CreateReservationHandler = Depends(get_create_reservation_handler),
) -> ResponseEnvelope[ReservationResponse]:
    repo = handler._reservation_repo  # type: ignore[attr-defined]
    reservation = await repo.get_by_id(reservation_id)
    if not reservation:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Reservation not found")
    return ResponseEnvelope(data=ReservationResponse.model_validate(reservation))


@router.post("/reservations/{reservation_id}/confirm", response_model=ResponseEnvelope[dict])
async def confirm_reservation(
    reservation_id: uuid.UUID,
    request: ConfirmReservationRequest,
    _current_user: dict[str, Any] = Depends(require_roles("RESTAURANT_OWNER", "RESTAURANT_STAFF", "SUPER_ADMIN")),
    handler: ConfirmReservationHandler = Depends(get_confirm_reservation_handler),
) -> ResponseEnvelope[dict]:
    command = ConfirmReservationCommand(reservation_id=reservation_id, table_id=request.table_id)
    await handler.handle(command)
    return ResponseEnvelope(data={"message": "Reservation confirmed"})


@router.post("/reservations/{reservation_id}/seat", response_model=ResponseEnvelope[dict])
async def seat_reservation(
    reservation_id: uuid.UUID,
    _current_user: dict[str, Any] = Depends(require_roles("RESTAURANT_OWNER", "RESTAURANT_STAFF", "SUPER_ADMIN")),
    handler: SeatReservationHandler = Depends(get_seat_reservation_handler),
) -> ResponseEnvelope[dict]:
    command = SeatReservationCommand(reservation_id=reservation_id)
    await handler.handle(command)
    return ResponseEnvelope(data={"message": "Guest seated"})


@router.post("/reservations/{reservation_id}/cancel", response_model=ResponseEnvelope[dict])
async def cancel_reservation(
    reservation_id: uuid.UUID,
    request: CancelReservationRequest,
    handler: CancelReservationHandler = Depends(get_cancel_reservation_handler),
) -> ResponseEnvelope[dict]:
    command = CancelReservationCommand(reservation_id=reservation_id, reason=request.reason)
    await handler.handle(command)
    return ResponseEnvelope(data={"message": "Reservation cancelled"})


@router.post("/reservations/{reservation_id}/no-show", response_model=ResponseEnvelope[dict])
async def mark_no_show(
    reservation_id: uuid.UUID,
    _current_user: dict[str, Any] = Depends(require_roles("RESTAURANT_OWNER", "RESTAURANT_STAFF", "SUPER_ADMIN")),
    handler: MarkNoShowHandler = Depends(get_mark_no_show_handler),
) -> ResponseEnvelope[dict]:
    command = MarkNoShowCommand(reservation_id=reservation_id)
    await handler.handle(command)
    return ResponseEnvelope(data={"message": "Reservation marked as no-show"})


# ---------------------------------------------------------------------------
# Waitlist
# ---------------------------------------------------------------------------


@router.post("/waitlist", response_model=ResponseEnvelope[dict], status_code=status.HTTP_201_CREATED)
async def join_waitlist(
    request: JoinWaitlistRequest,
    handler: JoinWaitlistHandler = Depends(get_join_waitlist_handler),
) -> ResponseEnvelope[dict]:
    command = JoinWaitlistCommand(
        restaurant_id=request.restaurant_id,
        customer_name=request.customer_name,
        customer_phone=request.customer_phone,
        party_size=request.party_size,
        preferred_section=request.preferred_section,
        special_requests=request.special_requests,
    )
    entry_id = await handler.handle(command)
    return ResponseEnvelope(data={"id": str(entry_id), "message": "Added to waitlist"})


@router.get("/waitlist", response_model=ResponseEnvelope[WaitlistListResponse])
async def list_waitlist(
    restaurant_id: uuid.UUID = Query(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    handler: JoinWaitlistHandler = Depends(get_join_waitlist_handler),
) -> ResponseEnvelope[WaitlistListResponse]:
    repo = handler._waitlist_repo  # type: ignore[attr-defined]
    entries = await repo.list_active_by_restaurant(restaurant_id, skip=skip, limit=limit)
    total = await repo.count_active_by_restaurant(restaurant_id)
    items = [WaitlistEntryResponse.model_validate(e) for e in entries]
    return ResponseEnvelope(data=WaitlistListResponse(items=items, total=total))


@router.post("/waitlist/{entry_id}/notify", response_model=ResponseEnvelope[dict])
async def notify_waitlist(
    entry_id: uuid.UUID,
    _current_user: dict[str, Any] = Depends(require_roles("RESTAURANT_OWNER", "RESTAURANT_STAFF", "SUPER_ADMIN")),
    handler: NotifyWaitlistHandler = Depends(get_notify_waitlist_handler),
) -> ResponseEnvelope[dict]:
    command = NotifyWaitlistCommand(waitlist_entry_id=entry_id)
    await handler.handle(command)
    return ResponseEnvelope(data={"message": "Customer notified"})


@router.post("/waitlist/{entry_id}/seat", response_model=ResponseEnvelope[dict])
async def seat_from_waitlist(
    entry_id: uuid.UUID,
    table_id: uuid.UUID = Query(...),
    _current_user: dict[str, Any] = Depends(require_roles("RESTAURANT_OWNER", "RESTAURANT_STAFF", "SUPER_ADMIN")),
    handler: SeatFromWaitlistHandler = Depends(get_seat_from_waitlist_handler),
) -> ResponseEnvelope[dict]:
    command = SeatFromWaitlistCommand(waitlist_entry_id=entry_id, table_id=table_id)
    await handler.handle(command)
    return ResponseEnvelope(data={"message": "Customer seated from waitlist"})


@router.delete("/waitlist/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_waitlist(
    entry_id: uuid.UUID,
    _current_user: dict[str, Any] = Depends(require_roles("RESTAURANT_OWNER", "RESTAURANT_STAFF", "SUPER_ADMIN")),
    handler: RemoveFromWaitlistHandler = Depends(get_remove_from_waitlist_handler),
) -> None:
    command = RemoveFromWaitlistCommand(waitlist_entry_id=entry_id)
    await handler.handle(command)
