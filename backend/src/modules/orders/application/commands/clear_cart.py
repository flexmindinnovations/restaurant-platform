import uuid
from dataclasses import dataclass

from modules.orders.application.ports.cart_repository import CartRepository


@dataclass(frozen=True)
class ClearCartCommand:
    customer_id: uuid.UUID


class ClearCartHandler:
    def __init__(self, cart_repo: CartRepository) -> None:
        self._cart_repo = cart_repo

    async def handle(self, command: ClearCartCommand) -> None:
        cart = await self._cart_repo.get_by_customer_id(command.customer_id)
        if not cart:
            return  # Idempotent

        cart.clear()
        await self._cart_repo.save(cart)
