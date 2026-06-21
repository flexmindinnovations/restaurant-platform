from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db_session
from modules.tables.application.commands.cancel_reservation import CancelReservationHandler
from modules.tables.application.commands.confirm_reservation import ConfirmReservationHandler
from modules.tables.application.commands.create_reservation import CreateReservationHandler
from modules.tables.application.commands.create_section import CreateSectionHandler
from modules.tables.application.commands.create_table import CreateTableHandler
from modules.tables.application.commands.delete_section import DeleteSectionHandler
from modules.tables.application.commands.delete_table import DeleteTableHandler
from modules.tables.application.commands.join_waitlist import JoinWaitlistHandler
from modules.tables.application.commands.mark_no_show import MarkNoShowHandler
from modules.tables.application.commands.notify_waitlist import NotifyWaitlistHandler
from modules.tables.application.commands.remove_from_waitlist import RemoveFromWaitlistHandler
from modules.tables.application.commands.seat_from_waitlist import SeatFromWaitlistHandler
from modules.tables.application.commands.seat_reservation import SeatReservationHandler
from modules.tables.application.commands.update_section import UpdateSectionHandler
from modules.tables.application.commands.update_table import UpdateTableHandler
from modules.tables.application.commands.update_table_status import UpdateTableStatusHandler
from modules.tables.domain.services.availability_service import TimeSlotAvailabilityService
from modules.tables.infrastructure.repositories.reservation_repository import SqlAlchemyReservationRepository
from modules.tables.infrastructure.repositories.section_repository import SqlAlchemySectionRepository
from modules.tables.infrastructure.repositories.table_repository import SqlAlchemyTableRepository
from modules.tables.infrastructure.repositories.waitlist_repository import SqlAlchemyWaitlistRepository
from shared.infrastructure.event_bus import get_event_bus
from shared.infrastructure.unit_of_work import SqlAlchemyUnitOfWork


# --- Repository factories ---


def _section_repo(session: AsyncSession = Depends(get_db_session)) -> SqlAlchemySectionRepository:
    return SqlAlchemySectionRepository(session)


def _table_repo(session: AsyncSession = Depends(get_db_session)) -> SqlAlchemyTableRepository:
    return SqlAlchemyTableRepository(session)


def _reservation_repo(session: AsyncSession = Depends(get_db_session)) -> SqlAlchemyReservationRepository:
    return SqlAlchemyReservationRepository(session)


def _waitlist_repo(session: AsyncSession = Depends(get_db_session)) -> SqlAlchemyWaitlistRepository:
    return SqlAlchemyWaitlistRepository(session)


def _uow(session: AsyncSession = Depends(get_db_session)) -> SqlAlchemyUnitOfWork:
    return SqlAlchemyUnitOfWork(session, get_event_bus())


def _availability_service() -> TimeSlotAvailabilityService:
    return TimeSlotAvailabilityService()


# --- Section handlers ---


def get_create_section_handler(
    section_repo: SqlAlchemySectionRepository = Depends(_section_repo),
    uow: SqlAlchemyUnitOfWork = Depends(_uow),
) -> CreateSectionHandler:
    return CreateSectionHandler(section_repo, uow)


def get_update_section_handler(
    section_repo: SqlAlchemySectionRepository = Depends(_section_repo),
    uow: SqlAlchemyUnitOfWork = Depends(_uow),
) -> UpdateSectionHandler:
    return UpdateSectionHandler(section_repo, uow)


def get_delete_section_handler(
    section_repo: SqlAlchemySectionRepository = Depends(_section_repo),
    uow: SqlAlchemyUnitOfWork = Depends(_uow),
) -> DeleteSectionHandler:
    return DeleteSectionHandler(section_repo, uow)


# --- Table handlers ---


def get_create_table_handler(
    table_repo: SqlAlchemyTableRepository = Depends(_table_repo),
    uow: SqlAlchemyUnitOfWork = Depends(_uow),
) -> CreateTableHandler:
    return CreateTableHandler(table_repo, uow)


def get_update_table_handler(
    table_repo: SqlAlchemyTableRepository = Depends(_table_repo),
    uow: SqlAlchemyUnitOfWork = Depends(_uow),
) -> UpdateTableHandler:
    return UpdateTableHandler(table_repo, uow)


def get_update_table_status_handler(
    table_repo: SqlAlchemyTableRepository = Depends(_table_repo),
    uow: SqlAlchemyUnitOfWork = Depends(_uow),
) -> UpdateTableStatusHandler:
    return UpdateTableStatusHandler(table_repo, uow)


def get_delete_table_handler(
    table_repo: SqlAlchemyTableRepository = Depends(_table_repo),
    uow: SqlAlchemyUnitOfWork = Depends(_uow),
) -> DeleteTableHandler:
    return DeleteTableHandler(table_repo, uow)


# --- Reservation handlers ---


def get_create_reservation_handler(
    reservation_repo: SqlAlchemyReservationRepository = Depends(_reservation_repo),
    table_repo: SqlAlchemyTableRepository = Depends(_table_repo),
    availability_service: TimeSlotAvailabilityService = Depends(_availability_service),
    uow: SqlAlchemyUnitOfWork = Depends(_uow),
) -> CreateReservationHandler:
    return CreateReservationHandler(reservation_repo, table_repo, availability_service, uow)


def get_confirm_reservation_handler(
    reservation_repo: SqlAlchemyReservationRepository = Depends(_reservation_repo),
    table_repo: SqlAlchemyTableRepository = Depends(_table_repo),
    uow: SqlAlchemyUnitOfWork = Depends(_uow),
) -> ConfirmReservationHandler:
    return ConfirmReservationHandler(reservation_repo, table_repo, uow)


def get_cancel_reservation_handler(
    reservation_repo: SqlAlchemyReservationRepository = Depends(_reservation_repo),
    uow: SqlAlchemyUnitOfWork = Depends(_uow),
) -> CancelReservationHandler:
    return CancelReservationHandler(reservation_repo, uow)


def get_seat_reservation_handler(
    reservation_repo: SqlAlchemyReservationRepository = Depends(_reservation_repo),
    table_repo: SqlAlchemyTableRepository = Depends(_table_repo),
    uow: SqlAlchemyUnitOfWork = Depends(_uow),
) -> SeatReservationHandler:
    return SeatReservationHandler(reservation_repo, table_repo, uow)


def get_mark_no_show_handler(
    reservation_repo: SqlAlchemyReservationRepository = Depends(_reservation_repo),
    uow: SqlAlchemyUnitOfWork = Depends(_uow),
) -> MarkNoShowHandler:
    return MarkNoShowHandler(reservation_repo, uow)


# --- Waitlist handlers ---


def get_join_waitlist_handler(
    waitlist_repo: SqlAlchemyWaitlistRepository = Depends(_waitlist_repo),
    uow: SqlAlchemyUnitOfWork = Depends(_uow),
) -> JoinWaitlistHandler:
    return JoinWaitlistHandler(waitlist_repo, uow)


def get_notify_waitlist_handler(
    waitlist_repo: SqlAlchemyWaitlistRepository = Depends(_waitlist_repo),
    uow: SqlAlchemyUnitOfWork = Depends(_uow),
) -> NotifyWaitlistHandler:
    return NotifyWaitlistHandler(waitlist_repo, uow)


def get_seat_from_waitlist_handler(
    waitlist_repo: SqlAlchemyWaitlistRepository = Depends(_waitlist_repo),
    table_repo: SqlAlchemyTableRepository = Depends(_table_repo),
    uow: SqlAlchemyUnitOfWork = Depends(_uow),
) -> SeatFromWaitlistHandler:
    return SeatFromWaitlistHandler(waitlist_repo, table_repo, uow)


def get_remove_from_waitlist_handler(
    waitlist_repo: SqlAlchemyWaitlistRepository = Depends(_waitlist_repo),
    uow: SqlAlchemyUnitOfWork = Depends(_uow),
) -> RemoveFromWaitlistHandler:
    return RemoveFromWaitlistHandler(waitlist_repo, uow)
