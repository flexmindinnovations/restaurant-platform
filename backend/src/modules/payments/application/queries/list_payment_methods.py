import uuid
from dataclasses import dataclass

from modules.payments.application.ports.payment_method_repository import PaymentMethodRepository


@dataclass
class PaymentMethodDTO:
    id: uuid.UUID
    customer_id: uuid.UUID
    type: str
    last_four: str | None
    brand: str | None
    is_default: bool
    token: str

    @classmethod
    def from_entity(cls, m) -> "PaymentMethodDTO":
        return cls(
            id=m.id,
            customer_id=m.customer_id,
            type=m.type,
            last_four=m.last_four,
            brand=m.brand,
            is_default=m.is_default,
            token=m.token,
        )


@dataclass(frozen=True)
class ListCustomerPaymentMethodsQuery:
    customer_id: uuid.UUID


class ListCustomerPaymentMethodsHandler:
    def __init__(self, payment_method_repo: PaymentMethodRepository) -> None:
        self._payment_method_repo = payment_method_repo

    async def handle(self, query: ListCustomerPaymentMethodsQuery) -> list[PaymentMethodDTO]:
        methods = await self._payment_method_repo.list_by_customer_id(query.customer_id)
        return [PaymentMethodDTO.from_entity(m) for m in methods]
