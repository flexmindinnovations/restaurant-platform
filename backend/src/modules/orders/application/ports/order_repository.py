import abc
import uuid

from modules.orders.domain.entities.order import Order
from modules.orders.domain.value_objects.order_status import OrderStatus


class OrderRepository(abc.ABC):
    @abc.abstractmethod
    async def add(self, order: Order) -> None:
        pass

    @abc.abstractmethod
    async def get_by_id(self, order_id: uuid.UUID) -> Order | None:
        pass

    @abc.abstractmethod
    async def get_by_order_number(self, order_number: str) -> Order | None:
        pass

    @abc.abstractmethod
    async def update(self, order: Order) -> None:
        pass

    @abc.abstractmethod
    async def list_by_customer(self, customer_id: uuid.UUID, skip: int = 0, limit: int = 10) -> tuple[list[Order], int]:
        pass

    @abc.abstractmethod
    async def list_by_restaurant(
        self,
        restaurant_id: uuid.UUID,
        status: OrderStatus | None = None,
        skip: int = 0,
        limit: int = 10,
    ) -> tuple[list[Order], int]:
        pass
