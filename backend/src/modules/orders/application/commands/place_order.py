import uuid
from dataclasses import dataclass
from decimal import Decimal

from modules.orders.application.ports.cart_repository import CartRepository
from modules.orders.application.ports.order_repository import OrderRepository
from modules.orders.domain.entities.order import Order
from modules.orders.domain.entities.order_item import OrderItem
from shared.application.ports.unit_of_work import AbstractUnitOfWork
from shared.domain.exceptions import ValidationException
from shared.domain.value_objects import Money


@dataclass(frozen=True)
class PlaceOrderCommand:
    customer_id: uuid.UUID
    delivery_address_street: str
    delivery_address_city: str
    delivery_address_state: str
    delivery_address_postal_code: str
    delivery_address_country: str
    tip_amount: Decimal
    delivery_notes: str | None = None


class PlaceOrderHandler:
    def __init__(
        self,
        order_repo: OrderRepository,
        cart_repo: CartRepository,
        uow: AbstractUnitOfWork,
    ) -> None:
        self._order_repo = order_repo
        self._cart_repo = cart_repo
        self._uow = uow

    async def handle(self, command: PlaceOrderCommand) -> uuid.UUID:
        # 1. Retrieve cart
        cart = await self._cart_repo.get_by_customer_id(command.customer_id)
        if not cart or not cart.items:
            raise ValidationException("Cart is empty")

        restaurant_id = cart.restaurant_id
        if not restaurant_id:
            raise ValidationException("Invalid cart: missing restaurant ID")

        # 2. Compute financial breakdowns
        subtotal = cart.total_amount
        currency = subtotal.currency

        # Calculate 8% tax, rounded to 2 decimal places
        tax_amount = (subtotal.amount * Decimal("0.08")).quantize(Decimal("0.01"))
        tax = Money(amount=tax_amount, currency=currency)

        # Flat $3.99 delivery fee
        delivery_fee = Money(amount=Decimal("3.99"), currency=currency)

        tip = Money(amount=command.tip_amount, currency=currency)

        # 3. Map cart items to order items
        # We need a temporary order ID to create OrderItems
        order_id = uuid.uuid4()
        order_items = [
            OrderItem.create(
                order_id=order_id,
                menu_item_id=item.menu_item_id,
                name=item.name,
                unit_price=item.unit_price,
                quantity=item.quantity,
                special_instructions=item.special_instructions,
            )
            for item in cart.items
        ]

        async with self._uow:
            # 4. Place order
            order = Order.place(
                restaurant_id=restaurant_id,
                customer_id=command.customer_id,
                items=order_items,
                delivery_address_street=command.delivery_address_street,
                delivery_address_city=command.delivery_address_city,
                delivery_address_state=command.delivery_address_state,
                delivery_address_postal_code=command.delivery_address_postal_code,
                delivery_address_country=command.delivery_address_country,
                subtotal=subtotal,
                tax=tax,
                delivery_fee=delivery_fee,
                tip=tip,
                delivery_notes=command.delivery_notes,
            )

            # Override random UUID with the pre-calculated one so OrderItems match the Order
            order.id = order_id

            # Save the new order
            await self._order_repo.add(order)
            self._uow.register_aggregate(order)

            # Clear the cart and save it
            cart.clear()
            await self._cart_repo.save(cart)

            # Commit the UoW transaction
            await self._uow.commit()

        return order.id
