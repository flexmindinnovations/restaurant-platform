import abc
import uuid

from modules.payments.domain.entities.payment_method import PaymentMethod


class PaymentMethodRepository(abc.ABC):
    @abc.abstractmethod
    async def add(self, payment_method: PaymentMethod) -> None:
        pass

    @abc.abstractmethod
    async def delete(self, payment_method_id: uuid.UUID) -> None:
        pass

    @abc.abstractmethod
    async def list_by_customer_id(self, customer_id: uuid.UUID) -> list[PaymentMethod]:
        pass

    @abc.abstractmethod
    async def get_by_id(self, payment_method_id: uuid.UUID) -> PaymentMethod | None:
        pass
