import uuid
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.tables.application.ports.reservation_repository import ReservationRepository
from modules.tables.domain.entities.reservation import Reservation
from modules.tables.domain.value_objects.reservation_source import ReservationSource
from modules.tables.domain.value_objects.reservation_status import ReservationStatus
from modules.tables.infrastructure.models.table_models import ReservationModel


class SqlAlchemyReservationRepository(ReservationRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, reservation: Reservation) -> None:
        model = ReservationModel(
            id=reservation.id,
            restaurant_id=reservation.restaurant_id,
            table_id=reservation.table_id,
            customer_id=reservation.customer_id,
            customer_name=reservation.customer_name,
            customer_phone=reservation.customer_phone,
            customer_email=reservation.customer_email,
            date=reservation.date,
            start_time=reservation.start_time,
            end_time=reservation.end_time,
            party_size=reservation.party_size,
            status=reservation.status.value,
            special_requests=reservation.special_requests,
            internal_notes=reservation.internal_notes,
            hold_until=reservation.hold_until,
            seated_at=reservation.seated_at,
            completed_at=reservation.completed_at,
            cancelled_at=reservation.cancelled_at,
            cancellation_reason=reservation.cancellation_reason,
            source=reservation.source.value,
            created_at=reservation.created_at,
            updated_at=reservation.updated_at,
        )
        self._session.add(model)

    async def get_by_id(self, reservation_id: uuid.UUID) -> Reservation | None:
        result = await self._session.execute(
            select(ReservationModel).where(ReservationModel.id == reservation_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_domain(model)

    async def update(self, reservation: Reservation) -> None:
        result = await self._session.execute(
            select(ReservationModel).where(ReservationModel.id == reservation.id)
        )
        model = result.scalar_one_or_none()
        if model:
            model.table_id = reservation.table_id
            model.customer_name = reservation.customer_name
            model.customer_phone = reservation.customer_phone
            model.customer_email = reservation.customer_email
            model.date = reservation.date
            model.start_time = reservation.start_time
            model.end_time = reservation.end_time
            model.party_size = reservation.party_size
            model.status = reservation.status.value
            model.special_requests = reservation.special_requests
            model.internal_notes = reservation.internal_notes
            model.hold_until = reservation.hold_until
            model.seated_at = reservation.seated_at
            model.completed_at = reservation.completed_at
            model.cancelled_at = reservation.cancelled_at
            model.cancellation_reason = reservation.cancellation_reason
            model.source = reservation.source.value
            model.updated_at = reservation.updated_at

    async def list_by_restaurant(
        self,
        restaurant_id: uuid.UUID,
        reservation_date: date | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Reservation]:
        query = select(ReservationModel).where(ReservationModel.restaurant_id == restaurant_id)
        if reservation_date is not None:
            query = query.where(ReservationModel.date == reservation_date)
        query = query.order_by(ReservationModel.date.desc(), ReservationModel.start_time).offset(skip).limit(limit)
        result = await self._session.execute(query)
        return [self._to_domain(m) for m in result.scalars().all()]

    async def list_by_table(
        self,
        table_id: uuid.UUID,
        reservation_date: date,
    ) -> list[Reservation]:
        query = (
            select(ReservationModel)
            .where(ReservationModel.table_id == table_id, ReservationModel.date == reservation_date)
            .order_by(ReservationModel.start_time)
        )
        result = await self._session.execute(query)
        return [self._to_domain(m) for m in result.scalars().all()]

    async def count_by_restaurant(
        self,
        restaurant_id: uuid.UUID,
        reservation_date: date | None = None,
    ) -> int:
        query = select(func.count(ReservationModel.id)).where(
            ReservationModel.restaurant_id == restaurant_id
        )
        if reservation_date is not None:
            query = query.where(ReservationModel.date == reservation_date)
        result = await self._session.execute(query)
        return result.scalar_one()

    def _to_domain(self, model: ReservationModel) -> Reservation:
        return Reservation(
            id=model.id,
            restaurant_id=model.restaurant_id,
            table_id=model.table_id,
            customer_id=model.customer_id,
            customer_name=model.customer_name,
            customer_phone=model.customer_phone,
            customer_email=model.customer_email,
            date=model.date,
            start_time=model.start_time,
            end_time=model.end_time,
            party_size=model.party_size,
            status=ReservationStatus(model.status),
            special_requests=model.special_requests,
            internal_notes=model.internal_notes,
            hold_until=model.hold_until,
            seated_at=model.seated_at,
            completed_at=model.completed_at,
            cancelled_at=model.cancelled_at,
            cancellation_reason=model.cancellation_reason,
            source=ReservationSource(model.source),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
