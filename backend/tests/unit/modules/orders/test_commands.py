import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from modules.orders.application.commands.add_to_cart import AddToCartCommand, AddToCartHandler
from modules.orders.application.commands.cancel_order import CancelOrderCommand, CancelOrderHandler
from modules.orders.application.commands.clear_cart import ClearCartCommand, ClearCartHandler
from modules.orders.application.commands.confirm_order import ConfirmOrderCommand, ConfirmOrderHandler
from modules.orders.application.commands.place_order import PlaceOrderCommand, PlaceOrderHandler
from modules.orders.application.commands.remove_from_cart import RemoveFromCartCommand, RemoveFromCartHandler
from modules.orders.application.commands.update_cart_item import UpdateCartItemCommand, UpdateCartItemHandler
from modules.orders.application.commands.update_order_status import UpdateOrderStatusCommand, UpdateOrderStatusHandler
from modules.orders.application.ports.menu_service import MenuItemDTO
from modules.orders.domain.entities.cart import Cart
from modules.orders.domain.entities.order import Order
from modules.orders.domain.entities.order_item import OrderItem
from modules.orders.domain.value_objects.order_status import OrderStatus
from shared.domain.exceptions import ValidationException
from shared.domain.value_objects import Money

# --- Helpers & Fixtures ---


class MockUow:
    def __init__(self):
        self.committed = False
        self.aggregates = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    def register_aggregate(self, aggregate):
        self.aggregates.append(aggregate)

    async def commit(self):
        self.committed = True


@pytest.fixture
def mock_cart_repo():
    repo = MagicMock()
    repo.get_by_customer_id = AsyncMock()
    repo.save = AsyncMock()
    repo.delete = AsyncMock()
    return repo


@pytest.fixture
def mock_order_repo():
    repo = MagicMock()
    repo.add = AsyncMock()
    repo.get_by_id = AsyncMock()
    repo.update = AsyncMock()
    return repo


@pytest.fixture
def mock_menu_service():
    service = MagicMock()
    service.get_menu_item = AsyncMock()
    return service


@pytest.fixture
def mock_uow():
    return MockUow()


# --- AddToCart Tests ---


@pytest.mark.asyncio
async def test_add_to_cart_success(mock_cart_repo, mock_menu_service):
    customer_id = uuid.uuid4()
    menu_item_id = uuid.uuid4()
    restaurant_id = uuid.uuid4()

    mock_menu_service.get_menu_item.return_value = MenuItemDTO(
        id=menu_item_id,
        restaurant_id=restaurant_id,
        name="Burger",
        price_amount=Decimal("10.00"),
        price_currency="INR",
        is_available=True,
    )
    mock_cart_repo.get_by_customer_id.return_value = None

    handler = AddToCartHandler(mock_cart_repo, mock_menu_service)
    cmd = AddToCartCommand(customer_id=customer_id, menu_item_id=menu_item_id, quantity=2)

    cart_id = await handler.handle(cmd)

    assert cart_id == customer_id
    mock_cart_repo.save.assert_called_once()
    saved_cart = mock_cart_repo.save.call_args[0][0]
    assert saved_cart.restaurant_id == restaurant_id
    assert len(saved_cart.items) == 1
    assert saved_cart.items[0].quantity == 2


@pytest.mark.asyncio
async def test_add_to_cart_item_not_found(mock_cart_repo, mock_menu_service):
    mock_menu_service.get_menu_item.return_value = None
    handler = AddToCartHandler(mock_cart_repo, mock_menu_service)
    cmd = AddToCartCommand(customer_id=uuid.uuid4(), menu_item_id=uuid.uuid4(), quantity=1)

    with pytest.raises(ValidationException, match="Menu item not found"):
        await handler.handle(cmd)


@pytest.mark.asyncio
async def test_add_to_cart_item_not_available(mock_cart_repo, mock_menu_service):
    mock_menu_service.get_menu_item.return_value = MenuItemDTO(
        id=uuid.uuid4(),
        restaurant_id=uuid.uuid4(),
        name="Burger",
        price_amount=Decimal("10.00"),
        price_currency="INR",
        is_available=False,
    )
    handler = AddToCartHandler(mock_cart_repo, mock_menu_service)
    cmd = AddToCartCommand(customer_id=uuid.uuid4(), menu_item_id=uuid.uuid4(), quantity=1)

    with pytest.raises(ValidationException, match="Menu item is not available"):
        await handler.handle(cmd)


# --- UpdateCartItem Tests ---


@pytest.mark.asyncio
async def test_update_cart_item_quantity(mock_cart_repo):
    customer_id = uuid.uuid4()
    menu_item_id = uuid.uuid4()
    cart = Cart.create(customer_id)
    cart.add_item(menu_item_id, "Burger", Money(Decimal("10.00"), "INR"), uuid.uuid4(), 1)

    mock_cart_repo.get_by_customer_id.return_value = cart

    handler = UpdateCartItemHandler(mock_cart_repo)
    cmd = UpdateCartItemCommand(customer_id=customer_id, menu_item_id=menu_item_id, quantity=3)

    await handler.handle(cmd)

    assert cart.items[0].quantity == 3
    mock_cart_repo.save.assert_called_once_with(cart)


# --- RemoveFromCart Tests ---


@pytest.mark.asyncio
async def test_remove_from_cart(mock_cart_repo):
    customer_id = uuid.uuid4()
    menu_item_id = uuid.uuid4()
    cart = Cart.create(customer_id)
    cart.add_item(menu_item_id, "Burger", Money(Decimal("10.00"), "INR"), uuid.uuid4(), 1)

    mock_cart_repo.get_by_customer_id.return_value = cart

    handler = RemoveFromCartHandler(mock_cart_repo)
    cmd = RemoveFromCartCommand(customer_id=customer_id, menu_item_id=menu_item_id)

    await handler.handle(cmd)

    assert len(cart.items) == 0
    mock_cart_repo.save.assert_called_once_with(cart)


# --- ClearCart Tests ---


@pytest.mark.asyncio
async def test_clear_cart(mock_cart_repo):
    customer_id = uuid.uuid4()
    cart = Cart.create(customer_id)
    cart.add_item(uuid.uuid4(), "Burger", Money(Decimal("10.00"), "INR"), uuid.uuid4(), 1)

    mock_cart_repo.get_by_customer_id.return_value = cart

    handler = ClearCartHandler(mock_cart_repo)
    cmd = ClearCartCommand(customer_id=customer_id)

    await handler.handle(cmd)

    assert len(cart.items) == 0
    mock_cart_repo.save.assert_called_once_with(cart)


# --- PlaceOrder Tests ---


@pytest.mark.asyncio
async def test_place_order_success(mock_order_repo, mock_cart_repo, mock_uow):
    customer_id = uuid.uuid4()
    restaurant_id = uuid.uuid4()
    cart = Cart.create(customer_id)
    cart.add_item(uuid.uuid4(), "Burger", Money(Decimal("10.00"), "INR"), restaurant_id, 2)

    mock_cart_repo.get_by_customer_id.return_value = cart

    handler = PlaceOrderHandler(mock_order_repo, mock_cart_repo, mock_uow)
    cmd = PlaceOrderCommand(
        customer_id=customer_id,
        delivery_address_street="123 Street",
        delivery_address_city="Seattle",
        delivery_address_state="WA",
        delivery_address_postal_code="98101",
        delivery_address_country="US",
        tip_amount=Decimal("3.00"),
        delivery_notes="Dropoff at lobby",
    )

    order_id = await handler.handle(cmd)

    assert order_id is not None
    mock_order_repo.add.assert_called_once()
    assert mock_uow.committed
    assert len(cart.items) == 0  # Cart cleared
    mock_cart_repo.save.assert_called_once_with(cart)


@pytest.mark.asyncio
async def test_place_order_empty_cart(mock_order_repo, mock_cart_repo, mock_uow):
    customer_id = uuid.uuid4()
    mock_cart_repo.get_by_customer_id.return_value = None

    handler = PlaceOrderHandler(mock_order_repo, mock_cart_repo, mock_uow)
    cmd = PlaceOrderCommand(
        customer_id=customer_id,
        delivery_address_street="123 Street",
        delivery_address_city="Seattle",
        delivery_address_state="WA",
        delivery_address_postal_code="98101",
        delivery_address_country="US",
        tip_amount=Decimal("3.00"),
    )

    with pytest.raises(ValidationException, match="Cart is empty"):
        await handler.handle(cmd)


# --- ConfirmOrder Tests ---


@pytest.mark.asyncio
async def test_confirm_order_success(mock_order_repo, mock_uow):
    order_id = uuid.uuid4()
    order_item = OrderItem(
        id=uuid.uuid4(),
        menu_item_id=uuid.uuid4(),
        name="Burger",
        unit_price=Money(Decimal("10.00"), "INR"),
        quantity=1,
    )
    order = Order.place(
        restaurant_id=uuid.uuid4(),
        customer_id=uuid.uuid4(),
        items=[order_item],
        delivery_address_street="123 Street",
        delivery_address_city="Seattle",
        delivery_address_state="WA",
        delivery_address_postal_code="98101",
        delivery_address_country="US",
        subtotal=Money(Decimal("10.00"), "INR"),
        tax=Money(Decimal("0.80"), "INR"),
        delivery_fee=Money(Decimal("49"), "INR"),
        tip=Money(Decimal("2.00"), "INR"),
    )
    mock_order_repo.get_by_id.return_value = order

    handler = ConfirmOrderHandler(mock_order_repo, mock_uow)
    cmd = ConfirmOrderCommand(order_id=order_id)

    await handler.handle(cmd)

    assert order.status == OrderStatus.CONFIRMED
    mock_order_repo.update.assert_called_once_with(order)
    assert mock_uow.committed


# --- UpdateOrderStatus Tests ---


@pytest.mark.asyncio
async def test_update_order_status(mock_order_repo, mock_uow):
    order_id = uuid.uuid4()
    order_item = OrderItem(
        id=uuid.uuid4(),
        menu_item_id=uuid.uuid4(),
        name="Burger",
        unit_price=Money(Decimal("10.00"), "INR"),
        quantity=1,
    )
    order = Order.place(
        restaurant_id=uuid.uuid4(),
        customer_id=uuid.uuid4(),
        items=[order_item],
        delivery_address_street="123 Street",
        delivery_address_city="Seattle",
        delivery_address_state="WA",
        delivery_address_postal_code="98101",
        delivery_address_country="US",
        subtotal=Money(Decimal("10.00"), "INR"),
        tax=Money(Decimal("0.80"), "INR"),
        delivery_fee=Money(Decimal("49"), "INR"),
        tip=Money(Decimal("2.00"), "INR"),
    )
    order.confirm()  # Must be confirmed before prepared

    mock_order_repo.get_by_id.return_value = order

    handler = UpdateOrderStatusHandler(mock_order_repo, mock_uow)
    cmd = UpdateOrderStatusCommand(order_id=order_id, status=OrderStatus.PREPARING)

    await handler.handle(cmd)

    assert order.status == OrderStatus.PREPARING
    mock_order_repo.update.assert_called_once_with(order)
    assert mock_uow.committed


# --- CancelOrder Tests ---


@pytest.mark.asyncio
async def test_cancel_order_customer_success(mock_order_repo, mock_uow):
    order_id = uuid.uuid4()
    customer_id = uuid.uuid4()
    order_item = OrderItem(
        id=uuid.uuid4(),
        menu_item_id=uuid.uuid4(),
        name="Burger",
        unit_price=Money(Decimal("10.00"), "INR"),
        quantity=1,
    )
    order = Order.place(
        restaurant_id=uuid.uuid4(),
        customer_id=customer_id,
        items=[order_item],
        delivery_address_street="123 Street",
        delivery_address_city="Seattle",
        delivery_address_state="WA",
        delivery_address_postal_code="98101",
        delivery_address_country="US",
        subtotal=Money(Decimal("10.00"), "INR"),
        tax=Money(Decimal("0.80"), "INR"),
        delivery_fee=Money(Decimal("49"), "INR"),
        tip=Money(Decimal("2.00"), "INR"),
    )

    mock_order_repo.get_by_id.return_value = order

    handler = CancelOrderHandler(mock_order_repo, mock_uow)
    cmd = CancelOrderCommand(
        order_id=order_id,
        reason="No longer hungry",
        user_id=customer_id,
        user_roles=["CUSTOMER"],
    )

    await handler.handle(cmd)

    assert order.status == OrderStatus.CANCELLED
    assert order.cancellation_reason == "No longer hungry"
    mock_order_repo.update.assert_called_once_with(order)
    assert mock_uow.committed


@pytest.mark.asyncio
async def test_cancel_order_customer_not_authorized(mock_order_repo, mock_uow):
    order_id = uuid.uuid4()
    customer_id = uuid.uuid4()
    order_item = OrderItem(
        id=uuid.uuid4(),
        menu_item_id=uuid.uuid4(),
        name="Burger",
        unit_price=Money(Decimal("10.00"), "INR"),
        quantity=1,
    )
    order = Order.place(
        restaurant_id=uuid.uuid4(),
        customer_id=customer_id,
        items=[order_item],
        delivery_address_street="123 Street",
        delivery_address_city="Seattle",
        delivery_address_state="WA",
        delivery_address_postal_code="98101",
        delivery_address_country="US",
        subtotal=Money(Decimal("10.00"), "INR"),
        tax=Money(Decimal("0.80"), "INR"),
        delivery_fee=Money(Decimal("49"), "INR"),
        tip=Money(Decimal("2.00"), "INR"),
    )

    mock_order_repo.get_by_id.return_value = order

    handler = CancelOrderHandler(mock_order_repo, mock_uow)
    # Different user ID and no admin/owner roles
    cmd = CancelOrderCommand(
        order_id=order_id,
        reason="Sneak cancel",
        user_id=uuid.uuid4(),
        user_roles=["CUSTOMER"],
    )

    with pytest.raises(ValidationException, match="Not authorized to cancel this order"):
        await handler.handle(cmd)


@pytest.mark.asyncio
async def test_cancel_order_customer_not_pending(mock_order_repo, mock_uow):
    order_id = uuid.uuid4()
    customer_id = uuid.uuid4()
    order_item = OrderItem(
        id=uuid.uuid4(),
        menu_item_id=uuid.uuid4(),
        name="Burger",
        unit_price=Money(Decimal("10.00"), "INR"),
        quantity=1,
    )
    order = Order.place(
        restaurant_id=uuid.uuid4(),
        customer_id=customer_id,
        items=[order_item],
        delivery_address_street="123 Street",
        delivery_address_city="Seattle",
        delivery_address_state="WA",
        delivery_address_postal_code="98101",
        delivery_address_country="US",
        subtotal=Money(Decimal("10.00"), "INR"),
        tax=Money(Decimal("0.80"), "INR"),
        delivery_fee=Money(Decimal("49"), "INR"),
        tip=Money(Decimal("2.00"), "INR"),
    )
    order.confirm()  # No longer in PENDING

    mock_order_repo.get_by_id.return_value = order

    handler = CancelOrderHandler(mock_order_repo, mock_uow)
    cmd = CancelOrderCommand(
        order_id=order_id,
        reason="No longer hungry",
        user_id=customer_id,
        user_roles=["CUSTOMER"],
    )

    with pytest.raises(ValidationException, match="Customer can only cancel orders in PENDING status"):
        await handler.handle(cmd)


@pytest.mark.asyncio
async def test_cancel_order_restaurant_owner_success(mock_order_repo, mock_uow):
    order_id = uuid.uuid4()
    customer_id = uuid.uuid4()
    order_item = OrderItem(
        id=uuid.uuid4(),
        menu_item_id=uuid.uuid4(),
        name="Burger",
        unit_price=Money(Decimal("10.00"), "INR"),
        quantity=1,
    )
    order = Order.place(
        restaurant_id=uuid.uuid4(),
        customer_id=customer_id,
        items=[order_item],
        delivery_address_street="123 Street",
        delivery_address_city="Seattle",
        delivery_address_state="WA",
        delivery_address_postal_code="98101",
        delivery_address_country="US",
        subtotal=Money(Decimal("10.00"), "INR"),
        tax=Money(Decimal("0.80"), "INR"),
        delivery_fee=Money(Decimal("49"), "INR"),
        tip=Money(Decimal("2.00"), "INR"),
    )
    order.confirm()  # Confirming

    mock_order_repo.get_by_id.return_value = order

    handler = CancelOrderHandler(mock_order_repo, mock_uow)
    # Different user id but has RESTAURANT_OWNER role
    cmd = CancelOrderCommand(
        order_id=order_id,
        reason="Out of stock",
        user_id=uuid.uuid4(),
        user_roles=["RESTAURANT_OWNER"],
    )

    await handler.handle(cmd)

    assert order.status == OrderStatus.CANCELLED
    assert order.cancellation_reason == "Out of stock"
    mock_order_repo.update.assert_called_once_with(order)
    assert mock_uow.committed
