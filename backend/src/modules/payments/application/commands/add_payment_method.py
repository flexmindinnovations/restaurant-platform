import uuid
from dataclasses import dataclass

from modules.payments.application.ports.payment_method_repository import PaymentMethodRepository
from modules.payments.domain.entities.payment_method import PaymentMethod
from shared.application.ports.unit_of_work import AbstractUnitOfWork


@dataclass(frozen=True)
class AddPaymentMethodCommand:
    customer_id: uuid.UUID
    type: str
    last_four: str | None
    brand: str | None
    is_default: bool
    token: str


class AddPaymentMethodHandler:
    def __init__(
        self,
        payment_method_repo: PaymentMethodRepository,
        uow: AbstractUnitOfWork,
    ) -> None:
        self._payment_method_repo = payment_method_repo
        self._uow = uow

    async def handle(self, command: AddPaymentMethodCommand) -> uuid.UUID:
        payment_method = PaymentMethod(
            id=uuid.uuid4(),
            customer_id=command.customer_id,
            type=command.type,
            last_four=command.last_four,
            brand=command.brand,
            is_default=command.is_default,
            token=command.token,
        )

        async with self._uow:
            # If default, remove default flag from other methods
            if command.is_default:
                existing_methods = await self._payment_method_repo.list_by_customer_id(command.customer_id)
                for method in existing_methods:
                    if method.is_default:
                        method.is_default = False
                        await self._payment_method_repo.add(method)

            await self._payment_method_repo.add(payment_method)
            self._uow.register_aggregate(payment_method)
            await self._uow.commit()

        return payment_method.id
