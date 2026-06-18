import abc
import uuid

from modules.payments.domain.entities.payment import Payment


class PaymentRepository(abc.ABC):
    @abc.abstractmethod
    async def add(self, payment: Payment) -> None:
        pass

    @abc.abstractmethod
    async def update(self, payment: Payment) -> None:
        pass

    @abc.abstractmethod
    async def get_by_id(self, payment_id: uuid.UUID) -> Payment | None:
        pass

    @abc.abstractmethod
    async def get_by_order_id(self, order_id: uuid.UUID) -> Payment | None:
        pass
