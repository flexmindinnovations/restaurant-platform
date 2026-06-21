import uuid
from abc import ABC, abstractmethod
from datetime import date

from modules.tables.domain.entities.reservation import Reservation


class ReservationRepository(ABC):
    @abstractmethod
    async def add(self, reservation: Reservation) -> None: ...

    @abstractmethod
    async def get_by_id(self, reservation_id: uuid.UUID) -> Reservation | None: ...

    @abstractmethod
    async def update(self, reservation: Reservation) -> None: ...

    @abstractmethod
    async def list_by_restaurant(
        self,
        restaurant_id: uuid.UUID,
        reservation_date: date | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Reservation]: ...

    @abstractmethod
    async def list_by_table(
        self,
        table_id: uuid.UUID,
        reservation_date: date,
    ) -> list[Reservation]: ...

    @abstractmethod
    async def count_by_restaurant(
        self,
        restaurant_id: uuid.UUID,
        reservation_date: date | None = None,
    ) -> int: ...
