import uuid
from dataclasses import dataclass

from modules.orders.application.ports.cart_repository import CartRepository
from modules.orders.application.ports.menu_service import MenuService
from modules.orders.domain.entities.cart import Cart
from shared.domain.exceptions import ValidationException
from shared.domain.value_objects import Money


@dataclass(frozen=True)
class AddToCartCommand:
    customer_id: uuid.UUID
    menu_item_id: uuid.UUID
    quantity: int
    special_instructions: str | None = None


class AddToCartHandler:
    def __init__(self, cart_repo: CartRepository, menu_service: MenuService) -> None:
        self._cart_repo = cart_repo
        self._menu_service = menu_service

    async def handle(self, command: AddToCartCommand) -> uuid.UUID:
        # 1. Fetch and validate menu item
        menu_item = await self._menu_service.get_menu_item(command.menu_item_id)
        if not menu_item:
            raise ValidationException("Menu item not found")
        if not menu_item.is_available:
            raise ValidationException("Menu item is not available")

        # 2. Fetch or create cart
        cart = await self._cart_repo.get_by_customer_id(command.customer_id)
        if not cart:
            cart = Cart.create(command.customer_id)

        # 3. Add item to cart
        price = Money(amount=menu_item.price_amount, currency=menu_item.price_currency)
        cart.add_item(
            menu_item_id=menu_item.id,
            name=menu_item.name,
            unit_price=price,
            restaurant_id=menu_item.restaurant_id,
            quantity=command.quantity,
            special_instructions=command.special_instructions,
        )

        # 4. Save cart
        await self._cart_repo.save(cart)
        return cart.id
