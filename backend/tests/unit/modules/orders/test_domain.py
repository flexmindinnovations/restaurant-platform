import uuid
from decimal import Decimal

import pytest

from modules.orders.domain.entities.cart import Cart
from modules.orders.domain.entities.order import Order
from modules.orders.domain.entities.order_item import OrderItem
from modules.orders.domain.events.order_events import (
    OrderCancelled,
    OrderCompleted,
    OrderConfirmed,
    OrderDelivered,
    OrderOutForDelivery,
    OrderPlaced,
    OrderPreparing,
    OrderReady,
)
from modules.orders.domain.value_objects.order_number import OrderNumber
from modules.orders.domain.value_objects.order_status import OrderStatus
from shared.domain.exceptions import ValidationException
from shared.domain.value_objects import Money


def test_cart_creation():
    customer_id = uuid.uuid4()
    cart = Cart.create(customer_id)
    assert cart.id == customer_id
    assert cart.restaurant_id is None
    assert len(cart.items) == 0
    assert cart.total_amount == Money(Decimal("0"))


def test_cart_add_item_success():
    customer_id = uuid.uuid4()
    restaurant_id = uuid.uuid4()
    menu_item_id = uuid.uuid4()
    cart = Cart.create(customer_id)

    cart.add_item(
        menu_item_id=menu_item_id,
        name="Pizza",
        unit_price=Money(Decimal("12.50"), "USD"),
        restaurant_id=restaurant_id,
        quantity=2,
        special_instructions="No onions",
    )

    assert cart.restaurant_id == restaurant_id
    assert len(cart.items) == 1
    assert cart.items[0].menu_item_id == menu_item_id
    assert cart.items[0].quantity == 2
    assert cart.items[0].special_instructions == "No onions"
    assert cart.total_amount == Money(Decimal("25.00"), "USD")


def test_cart_add_item_invalid_quantity():
    customer_id = uuid.uuid4()
    restaurant_id = uuid.uuid4()
    menu_item_id = uuid.uuid4()
    cart = Cart.create(customer_id)

    with pytest.raises(ValidationException, match="Quantity must be at least 1"):
        cart.add_item(
            menu_item_id=menu_item_id,
            name="Pizza",
            unit_price=Money(Decimal("12.50"), "USD"),
            restaurant_id=restaurant_id,
            quantity=0,
        )


def test_cart_add_item_different_restaurant():
    customer_id = uuid.uuid4()
    restaurant_id_1 = uuid.uuid4()
    restaurant_id_2 = uuid.uuid4()
    cart = Cart.create(customer_id)

    cart.add_item(
        menu_item_id=uuid.uuid4(),
        name="Pizza",
        unit_price=Money(Decimal("12.50"), "USD"),
        restaurant_id=restaurant_id_1,
        quantity=1,
    )

    with pytest.raises(ValidationException, match="Cannot add items from a different restaurant"):
        cart.add_item(
            menu_item_id=uuid.uuid4(),
            name="Burger",
            unit_price=Money(Decimal("8.50"), "USD"),
            restaurant_id=restaurant_id_2,
            quantity=1,
        )


def test_cart_add_identical_item_merges():
    customer_id = uuid.uuid4()
    restaurant_id = uuid.uuid4()
    menu_item_id = uuid.uuid4()
    cart = Cart.create(customer_id)

    cart.add_item(
        menu_item_id=menu_item_id,
        name="Pizza",
        unit_price=Money(Decimal("12.50"), "USD"),
        restaurant_id=restaurant_id,
        quantity=1,
        special_instructions="Extra cheese",
    )

    cart.add_item(
        menu_item_id=menu_item_id,
        name="Pizza",
        unit_price=Money(Decimal("12.50"), "USD"),
        restaurant_id=restaurant_id,
        quantity=2,
        special_instructions="Extra cheese",
    )

    assert len(cart.items) == 1
    assert cart.items[0].quantity == 3


def test_cart_remove_item():
    customer_id = uuid.uuid4()
    restaurant_id = uuid.uuid4()
    menu_item_id = uuid.uuid4()
    cart = Cart.create(customer_id)

    cart.add_item(
        menu_item_id=menu_item_id,
        name="Pizza",
        unit_price=Money(Decimal("12.50"), "USD"),
        restaurant_id=restaurant_id,
        quantity=1,
    )

    assert cart.restaurant_id == restaurant_id
    cart.remove_item(menu_item_id)
    assert len(cart.items) == 0
    assert cart.restaurant_id is None


def test_cart_update_quantity():
    customer_id = uuid.uuid4()
    restaurant_id = uuid.uuid4()
    menu_item_id = uuid.uuid4()
    cart = Cart.create(customer_id)

    cart.add_item(
        menu_item_id=menu_item_id,
        name="Pizza",
        unit_price=Money(Decimal("12.50"), "USD"),
        restaurant_id=restaurant_id,
        quantity=1,
    )

    cart.update_quantity(menu_item_id, 5)
    assert cart.items[0].quantity == 5

    # Update to 0 should remove the item
    cart.update_quantity(menu_item_id, 0)
    assert len(cart.items) == 0
    assert cart.restaurant_id is None


def test_cart_update_quantity_not_found():
    customer_id = uuid.uuid4()
    cart = Cart.create(customer_id)
    with pytest.raises(ValidationException, match="Item not found in cart"):
        cart.update_quantity(uuid.uuid4(), 3)


def test_cart_clear():
    customer_id = uuid.uuid4()
    restaurant_id = uuid.uuid4()
    cart = Cart.create(customer_id)

    cart.add_item(
        menu_item_id=uuid.uuid4(),
        name="Pizza",
        unit_price=Money(Decimal("12.50"), "USD"),
        restaurant_id=restaurant_id,
        quantity=1,
    )

    cart.clear()
    assert len(cart.items) == 0
    assert cart.restaurant_id is None


def test_place_order_success():
    restaurant_id = uuid.uuid4()
    customer_id = uuid.uuid4()
    item_id = uuid.uuid4()

    item = OrderItem(
        id=uuid.uuid4(),
        menu_item_id=item_id,
        name="Pizza",
        unit_price=Money(Decimal("15.00"), "USD"),
        quantity=2,
        special_instructions="Crispy",
    )

    order = Order.place(
        restaurant_id=restaurant_id,
        customer_id=customer_id,
        items=[item],
        delivery_address_street="123 Main St",
        delivery_address_city="Seattle",
        delivery_address_state="WA",
        delivery_address_postal_code="98101",
        delivery_address_country="US",
        subtotal=Money(Decimal("30.00"), "USD"),
        tax=Money(Decimal("3.00"), "USD"),
        delivery_fee=Money(Decimal("5.00"), "USD"),
        tip=Money(Decimal("2.00"), "USD"),
        delivery_notes="Leave at door",
    )

    assert order.restaurant_id == restaurant_id
    assert order.customer_id == customer_id
    assert order.status == OrderStatus.PENDING
    assert order.total_amount == Money(Decimal("40.00"), "USD")
    assert len(order._domain_events) == 1
    assert isinstance(order._domain_events[0], OrderPlaced)


def test_place_order_empty_items():
    with pytest.raises(ValidationException, match="Order must have at least one item"):
        Order.place(
            restaurant_id=uuid.uuid4(),
            customer_id=uuid.uuid4(),
            items=[],
            delivery_address_street="123 Main St",
            delivery_address_city="Seattle",
            delivery_address_state="WA",
            delivery_address_postal_code="98101",
            delivery_address_country="US",
            subtotal=Money(Decimal("0.00"), "USD"),
            tax=Money(Decimal("0.00"), "USD"),
            delivery_fee=Money(Decimal("0.00"), "USD"),
            tip=Money(Decimal("0.00"), "USD"),
        )


def test_place_order_currency_mismatch():
    restaurant_id = uuid.uuid4()
    customer_id = uuid.uuid4()
    item = OrderItem(
        id=uuid.uuid4(),
        menu_item_id=uuid.uuid4(),
        name="Pizza",
        unit_price=Money(Decimal("15.00"), "EUR"),
        quantity=1,
    )

    with pytest.raises(ValidationException, match="All items must have the same currency"):
        Order.place(
            restaurant_id=restaurant_id,
            customer_id=customer_id,
            items=[item],
            delivery_address_street="123 Main St",
            delivery_address_city="Seattle",
            delivery_address_state="WA",
            delivery_address_postal_code="98101",
            delivery_address_country="US",
            subtotal=Money(Decimal("15.00"), "USD"),
            tax=Money(Decimal("1.50"), "USD"),
            delivery_fee=Money(Decimal("5.00"), "USD"),
            tip=Money(Decimal("2.00"), "USD"),
        )

    item_usd = OrderItem(
        id=uuid.uuid4(),
        menu_item_id=uuid.uuid4(),
        name="Pizza",
        unit_price=Money(Decimal("15.00"), "USD"),
        quantity=1,
    )

    with pytest.raises(ValidationException, match="All charge amounts must have the same currency"):
        Order.place(
            restaurant_id=restaurant_id,
            customer_id=customer_id,
            items=[item_usd],
            delivery_address_street="123 Main St",
            delivery_address_city="Seattle",
            delivery_address_state="WA",
            delivery_address_postal_code="98101",
            delivery_address_country="US",
            subtotal=Money(Decimal("15.00"), "USD"),
            tax=Money(Decimal("1.50"), "EUR"),  # EUR mismatch
            delivery_fee=Money(Decimal("5.00"), "USD"),
            tip=Money(Decimal("2.00"), "USD"),
        )


def test_order_transitions():
    restaurant_id = uuid.uuid4()
    customer_id = uuid.uuid4()
    item = OrderItem(
        id=uuid.uuid4(),
        menu_item_id=uuid.uuid4(),
        name="Pizza",
        unit_price=Money(Decimal("15.00"), "USD"),
        quantity=1,
    )
    order = Order.place(
        restaurant_id=restaurant_id,
        customer_id=customer_id,
        items=[item],
        delivery_address_street="123 Main St",
        delivery_address_city="Seattle",
        delivery_address_state="WA",
        delivery_address_postal_code="98101",
        delivery_address_country="US",
        subtotal=Money(Decimal("15.00"), "USD"),
        tax=Money(Decimal("1.50"), "USD"),
        delivery_fee=Money(Decimal("2.00"), "USD"),
        tip=Money(Decimal("1.00"), "USD"),
    )

    # 1. PENDING -> CONFIRMED
    order.confirm()
    assert order.status == OrderStatus.CONFIRMED
    assert order.confirmed_at is not None
    assert any(isinstance(e, OrderConfirmed) for e in order._domain_events)

    # 2. CONFIRMED -> PREPARING
    order.start_preparing()
    assert order.status == OrderStatus.PREPARING
    assert order.preparing_at is not None
    assert any(isinstance(e, OrderPreparing) for e in order._domain_events)

    # 3. PREPARING -> READY
    order.mark_ready()
    assert order.status == OrderStatus.READY
    assert order.ready_at is not None
    assert any(isinstance(e, OrderReady) for e in order._domain_events)

    # 4. READY -> OUT_FOR_DELIVERY
    order.mark_picked_up()
    assert order.status == OrderStatus.OUT_FOR_DELIVERY
    assert order.picked_up_at is not None
    assert any(isinstance(e, OrderOutForDelivery) for e in order._domain_events)

    # 5. OUT_FOR_DELIVERY -> DELIVERED
    order.mark_delivered()
    assert order.status == OrderStatus.DELIVERED
    assert order.delivered_at is not None
    assert any(isinstance(e, OrderDelivered) for e in order._domain_events)

    # 6. DELIVERED -> COMPLETED
    order.complete()
    assert order.status == OrderStatus.COMPLETED
    assert any(isinstance(e, OrderCompleted) for e in order._domain_events)


def test_order_invalid_transitions():
    restaurant_id = uuid.uuid4()
    customer_id = uuid.uuid4()
    item = OrderItem(
        id=uuid.uuid4(),
        menu_item_id=uuid.uuid4(),
        name="Pizza",
        unit_price=Money(Decimal("15.00"), "USD"),
        quantity=1,
    )
    order = Order.place(
        restaurant_id=restaurant_id,
        customer_id=customer_id,
        items=[item],
        delivery_address_street="123 Main St",
        delivery_address_city="Seattle",
        delivery_address_state="WA",
        delivery_address_postal_code="98101",
        delivery_address_country="US",
        subtotal=Money(Decimal("15.00"), "USD"),
        tax=Money(Decimal("1.50"), "USD"),
        delivery_fee=Money(Decimal("2.00"), "USD"),
        tip=Money(Decimal("1.00"), "USD"),
    )

    # Cannot skip from PENDING to READY
    with pytest.raises(ValidationException, match="Cannot transition from PENDING to READY"):
        order.mark_ready()


def test_order_cancellation():
    restaurant_id = uuid.uuid4()
    customer_id = uuid.uuid4()
    item = OrderItem(
        id=uuid.uuid4(),
        menu_item_id=uuid.uuid4(),
        name="Pizza",
        unit_price=Money(Decimal("15.00"), "USD"),
        quantity=1,
    )
    order = Order.place(
        restaurant_id=restaurant_id,
        customer_id=customer_id,
        items=[item],
        delivery_address_street="123 Main St",
        delivery_address_city="Seattle",
        delivery_address_state="WA",
        delivery_address_postal_code="98101",
        delivery_address_country="US",
        subtotal=Money(Decimal("15.00"), "USD"),
        tax=Money(Decimal("1.50"), "USD"),
        delivery_fee=Money(Decimal("2.00"), "USD"),
        tip=Money(Decimal("1.00"), "USD"),
    )

    order.cancel("Customer changed mind")
    assert order.status == OrderStatus.CANCELLED
    assert order.cancellation_reason == "Customer changed mind"
    assert order.cancelled_at is not None
    assert any(isinstance(e, OrderCancelled) for e in order._domain_events)


def test_order_cancellation_non_cancellable():
    restaurant_id = uuid.uuid4()
    customer_id = uuid.uuid4()
    item = OrderItem(
        id=uuid.uuid4(),
        menu_item_id=uuid.uuid4(),
        name="Pizza",
        unit_price=Money(Decimal("15.00"), "USD"),
        quantity=1,
    )
    order = Order.place(
        restaurant_id=restaurant_id,
        customer_id=customer_id,
        items=[item],
        delivery_address_street="123 Main St",
        delivery_address_city="Seattle",
        delivery_address_state="WA",
        delivery_address_postal_code="98101",
        delivery_address_country="US",
        subtotal=Money(Decimal("15.00"), "USD"),
        tax=Money(Decimal("1.50"), "USD"),
        delivery_fee=Money(Decimal("2.00"), "USD"),
        tip=Money(Decimal("1.00"), "USD"),
    )

    order.confirm()
    order.start_preparing()
    # PREPARING is not cancellable
    with pytest.raises(ValidationException, match="Cannot cancel order in PREPARING status"):
        order.cancel("Prepared, too late")


def test_order_number_generation():
    on1 = OrderNumber.generate()
    on2 = OrderNumber.generate()
    assert on1.value.startswith("ORD-")
    assert len(on1.value) == 17  # ORD-YYYYMMDD-HEX (4+8+1+4) = 17
    assert on1.value != on2.value
