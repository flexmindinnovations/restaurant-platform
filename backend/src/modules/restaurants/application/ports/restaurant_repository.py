import uuid
from abc import ABC, abstractmethod

from modules.restaurants.domain.entities.restaurant import Restaurant


class RestaurantRepository(ABC):
    @abstractmethod
    async def add(self, restaurant: Restaurant) -> None:
        """Add a new restaurant."""

    @abstractmethod
    async def get_by_id(self, restaurant_id: uuid.UUID) -> Restaurant | None:
        """Retrieve a restaurant by ID."""

    @abstractmethod
    async def update(self, restaurant: Restaurant) -> None:
        """Update an existing restaurant."""

    @abstractmethod
    async def list_all(self, skip: int = 0, limit: int = 10, search: str | None = None) -> list[Restaurant]:
        """List restaurants with pagination and search."""

    @abstractmethod
    async def count_all(self, search: str | None = None) -> int:
        """Count total restaurants matching search criteria."""
