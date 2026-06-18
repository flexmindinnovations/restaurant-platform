import uuid
from decimal import Decimal

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from modules.deliveries.application.ports.partner_repository import PartnerRepository
from modules.deliveries.domain.entities.delivery_partner import DeliveryPartner
from modules.deliveries.domain.value_objects.location import GeoLocation
from modules.deliveries.domain.value_objects.vehicle_type import VehicleType
from modules.deliveries.infrastructure.models.delivery_models import DeliveryPartnerModel


class SqlAlchemyPartnerRepository(PartnerRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _row_to_entity(self, row) -> DeliveryPartner:
        model = row[0]
        lon = row[1]
        lat = row[2]

        current_loc = None
        if lon is not None and lat is not None:
            current_loc = GeoLocation(latitude=Decimal(str(lat)), longitude=Decimal(str(lon)))

        partner = DeliveryPartner(
            id=model.id,
            account_id=model.account_id,
            name=model.name,
            phone=model.phone,
            vehicle_type=VehicleType(model.vehicle_type),
            is_online=model.is_online,
            is_available=model.is_available,
            current_location=current_loc,
            rating_avg=Decimal(str(model.rating_avg)) if model.rating_avg is not None else Decimal("5.0"),
            total_deliveries=model.total_deliveries,
        )
        partner.created_at = model.created_at
        partner.updated_at = model.updated_at
        return partner

    async def add(self, partner: DeliveryPartner) -> None:
        model = DeliveryPartnerModel(
            id=partner.id,
            account_id=partner.account_id,
            name=partner.name,
            phone=partner.phone,
            vehicle_type=partner.vehicle_type.value if hasattr(partner.vehicle_type, "value") else str(
                partner.vehicle_type
            ),
            is_online=partner.is_online,
            is_available=partner.is_available,
            rating_avg=float(partner.rating_avg) if partner.rating_avg is not None else 5.0,
            total_deliveries=partner.total_deliveries,
            created_at=partner.created_at,
            updated_at=partner.updated_at,
        )
        if partner.current_location:
            loc = partner.current_location
            model.current_location = text(
                f"ST_GeogFromText('SRID=4326;POINT({loc.longitude} {loc.latitude})')"
            )

        self._session.add(model)

    async def update(self, partner: DeliveryPartner) -> None:
        result = await self._session.execute(
            select(DeliveryPartnerModel).where(DeliveryPartnerModel.id == partner.id)
        )
        model = result.scalar_one_or_none()
        if model:
            model.name = partner.name
            model.phone = partner.phone
            model.is_online = partner.is_online
            model.is_available = partner.is_available
            model.rating_avg = float(partner.rating_avg) if partner.rating_avg is not None else 5.0
            model.total_deliveries = partner.total_deliveries
            model.updated_at = partner.updated_at

            if partner.current_location:
                loc = partner.current_location
                model.current_location = text(
                    f"ST_GeogFromText('SRID=4326;POINT({loc.longitude} {loc.latitude})')"
                )
            else:
                model.current_location = None

    async def get_by_id(self, partner_id: uuid.UUID) -> DeliveryPartner | None:
        result = await self._session.execute(
            select(
                DeliveryPartnerModel,
                text("ST_X(current_location::geometry)"),
                text("ST_Y(current_location::geometry)"),
            ).where(DeliveryPartnerModel.id == partner_id)
        )
        row = result.first()
        return self._row_to_entity(row) if row else None

    async def get_by_account_id(self, account_id: uuid.UUID) -> DeliveryPartner | None:
        result = await self._session.execute(
            select(
                DeliveryPartnerModel,
                text("ST_X(current_location::geometry)"),
                text("ST_Y(current_location::geometry)"),
            ).where(DeliveryPartnerModel.account_id == account_id)
        )
        row = result.first()
        return self._row_to_entity(row) if row else None

    async def find_nearest_available(
        self,
        location: GeoLocation,
        radius_km: Decimal,
        limit: int = 5,
    ) -> list[DeliveryPartner]:
        lon = float(location.longitude)
        lat = float(location.latitude)
        radius_meters = float(radius_km) * 1000.0

        result = await self._session.execute(
            select(
                DeliveryPartnerModel,
                text("ST_X(current_location::geometry)"),
                text("ST_Y(current_location::geometry)"),
            ).where(
                DeliveryPartnerModel.is_online.is_(True),
                DeliveryPartnerModel.is_available.is_(True),
                text(
                    f"ST_DWithin(current_location, "
                    f"ST_SetSRID(ST_MakePoint({lon}, {lat}), 4326)::geography, "
                    f"{radius_meters})"
                )
            ).order_by(
                text(
                    f"ST_Distance(current_location, ST_SetSRID(ST_MakePoint({lon}, {lat}), 4326)::geography)"
                )
            ).limit(limit)
        )
        rows = result.all()
        return [self._row_to_entity(r) for r in rows]
