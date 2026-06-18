import uuid
from dataclasses import dataclass

from modules.orders.application.ports.cart_repository import CartRepository
from shared.domain.exceptions import ValidationException


@dataclass(frozen=True)
class RemoveFromCartCommand:
    customer_id: uuid.UUID
    menu_item_id: uuid.UUID


class RemoveFromCartHandler:
    def __init__(self, cart_repo: CartRepository) -> None:
        self._cart_repo = cart_repo

    async def handle(self, command: RemoveFromCartCommand) -> None:
        cart = await self._cart_repo.get_by_customer_id(command.customer_id)
        if not cart:
            raise ValidationException("Cart not found")

        cart.remove_item(command.menu_item_id)
        await self._cart_repo.save(cart)
