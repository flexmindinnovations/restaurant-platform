import uuid
from dataclasses import dataclass

from modules.restaurants.application.ports.restaurant_repository import RestaurantRepository
from shared.application.ports.unit_of_work import AbstractUnitOfWork
from shared.domain.exceptions import NotFoundException


@dataclass(frozen=True)
class VerifyRestaurantCommand:
    restaurant_id: uuid.UUID


class VerifyRestaurantHandler:
    def __init__(self, restaurant_repo: RestaurantRepository, uow: AbstractUnitOfWork) -> None:
        self._restaurant_repo = restaurant_repo
        self._uow = uow

    async def handle(self, command: VerifyRestaurantCommand) -> None:
        restaurant = await self._restaurant_repo.get_by_id(command.restaurant_id)
        if not restaurant:
            raise NotFoundException("Restaurant not found")

        restaurant.verify()

        async with self._uow:
            await self._restaurant_repo.update(restaurant)
            self._uow.register_aggregate(restaurant)
            await self._uow.commit()
