import abc
import uuid

from modules.orders.domain.entities.cart import Cart


class CartRepository(abc.ABC):
    @abc.abstractmethod
    async def get_by_customer_id(self, customer_id: uuid.UUID) -> Cart | None:
        pass

    @abc.abstractmethod
    async def save(self, cart: Cart) -> None:
        pass

    @abc.abstractmethod
    async def delete(self, customer_id: uuid.UUID) -> None:
        pass
