import math
from dataclasses import dataclass
from decimal import Decimal

from shared.domain.value_objects import ValueObject


@dataclass(frozen=True)
class GeoLocation(ValueObject):
    latitude: Decimal
    longitude: Decimal

    def distance_to(self, other: "GeoLocation") -> Decimal:
        """Calculate the great-circle distance between two points in kilometers.

        Uses the Haversine formula.
        """
        earth_radius_km = 6371.0

        lat1 = math.radians(float(self.latitude))
        lon1 = math.radians(float(self.longitude))
        lat2 = math.radians(float(other.latitude))
        lon2 = math.radians(float(other.longitude))

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        distance = earth_radius_km * c
        return Decimal(str(round(distance, 2)))
