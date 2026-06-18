import uuid
from dataclasses import dataclass

from modules.deliveries.application.ports.location_cache import LocationCache
from modules.deliveries.application.ports.partner_repository import PartnerRepository
from shared.domain.exceptions import ValidationException


@dataclass
class PartnerLocationDTO:
    partner_id: uuid.UUID
    latitude: float
    longitude: float


@dataclass(frozen=True)
class GetPartnerLocationQuery:
    partner_id: uuid.UUID


class GetPartnerLocationHandler:
    def __init__(
        self,
        partner_repo: PartnerRepository,
        location_cache: LocationCache,
    ) -> None:
        self._partner_repo = partner_repo
        self._location_cache = location_cache

    async def handle(self, query: GetPartnerLocationQuery) -> PartnerLocationDTO:
        loc = await self._location_cache.get_location(query.partner_id)
        if loc:
            return PartnerLocationDTO(
                partner_id=query.partner_id,
                latitude=float(loc.latitude),
                longitude=float(loc.longitude),
            )

        partner = await self._partner_repo.get_by_id(query.partner_id)
        if not partner:
            raise ValidationException("Partner not found")
        if not partner.current_location:
            raise ValidationException("No location available for partner")

        return PartnerLocationDTO(
            partner_id=query.partner_id,
            latitude=float(partner.current_location.latitude),
            longitude=float(partner.current_location.longitude),
        )
