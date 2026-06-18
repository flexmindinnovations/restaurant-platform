import uuid
from decimal import Decimal

import pytest

from modules.menus.domain.entities.category import Category
from modules.menus.domain.entities.menu import Menu
from modules.menus.domain.entities.menu_item import MenuItem
from shared.domain.exceptions import ValidationException
from shared.domain.value_objects import Money


@pytest.mark.unit
class TestMenu:
    def test_create_menu(self):
        restaurant_id = uuid.uuid4()
        menu = Menu.create(restaurant_id=restaurant_id, name="Lunch Menu", description="Daily lunch")

        assert menu.restaurant_id == restaurant_id
        assert menu.name == "Lunch Menu"
        assert menu.description == "Daily lunch"
        assert menu.is_active is False

        events = menu.collect_events()
        assert len(events) == 1
        assert events[0].__class__.__name__ == "MenuCreated"
        assert events[0].restaurant_id == restaurant_id

    def test_create_menu_empty_name_raises(self):
        with pytest.raises(ValidationException, match="Menu name cannot be empty"):
            Menu.create(restaurant_id=uuid.uuid4(), name="")

    def test_update_menu_details(self):
        menu = Menu.create(restaurant_id=uuid.uuid4(), name="Old Name")
        menu.collect_events()

        menu.update_details(name="New Name", description="Updated")

        assert menu.name == "New Name"
        assert menu.description == "Updated"
        events = menu.collect_events()
        assert any(e.__class__.__name__ == "MenuUpdated" for e in events)

    def test_update_menu_empty_name_raises(self):
        menu = Menu.create(restaurant_id=uuid.uuid4(), name="Valid")
        with pytest.raises(ValidationException, match="Menu name cannot be empty"):
            menu.update_details(name="")

    def test_publish_menu(self):
        menu = Menu.create(restaurant_id=uuid.uuid4(), name="Test")
        menu.collect_events()

        menu.publish()

        assert menu.is_active is True
        events = menu.collect_events()
        assert any(e.__class__.__name__ == "MenuPublished" for e in events)

    def test_publish_menu_idempotent(self):
        menu = Menu.create(restaurant_id=uuid.uuid4(), name="Test")
        menu.publish()
        menu.collect_events()

        menu.publish()
        assert menu.collect_events() == []

    def test_unpublish_menu(self):
        menu = Menu.create(restaurant_id=uuid.uuid4(), name="Test")
        menu.publish()
        menu.collect_events()

        menu.unpublish()

        assert menu.is_active is False
        events = menu.collect_events()
        assert any(e.__class__.__name__ == "MenuUnpublished" for e in events)


@pytest.mark.unit
class TestCategory:
    def test_create_category(self):
        menu_id = uuid.uuid4()
        category = Category.create(menu_id=menu_id, name="Appetizers", display_order=1)

        assert category.menu_id == menu_id
        assert category.name == "Appetizers"
        assert category.display_order == 1
        assert category.is_active is True

    def test_create_category_empty_name_raises(self):
        with pytest.raises(ValidationException, match="Category name cannot be empty"):
            Category.create(menu_id=uuid.uuid4(), name="")

    def test_update_category(self):
        category = Category.create(menu_id=uuid.uuid4(), name="Starters")
        category.update(name="Appetizers", display_order=2)

        assert category.name == "Appetizers"
        assert category.display_order == 2

    def test_deactivate_category(self):
        category = Category.create(menu_id=uuid.uuid4(), name="Drinks")
        category.deactivate()

        assert category.is_active is False


@pytest.mark.unit
class TestMenuItem:
    def _make_price(self, amount: str = "9.99") -> Money:
        return Money(amount=Decimal(amount))

    def test_create_menu_item(self):
        menu_id = uuid.uuid4()
        restaurant_id = uuid.uuid4()
        item = MenuItem.create(
            menu_id=menu_id,
            restaurant_id=restaurant_id,
            name="Burger",
            price=self._make_price("12.50"),
            dietary_labels=["gluten-free"],
            preparation_time_minutes=15,
        )

        assert item.menu_id == menu_id
        assert item.restaurant_id == restaurant_id
        assert item.name == "Burger"
        assert item.price.amount == Decimal("12.50")
        assert item.is_available is True
        assert item.dietary_labels == ["gluten-free"]
        assert item.preparation_time_minutes == 15

        events = item.collect_events()
        assert len(events) == 1
        assert events[0].__class__.__name__ == "MenuItemCreated"

    def test_create_item_empty_name_raises(self):
        with pytest.raises(ValidationException, match="Menu item name cannot be empty"):
            MenuItem.create(
                menu_id=uuid.uuid4(),
                restaurant_id=uuid.uuid4(),
                name="",
                price=self._make_price(),
            )

    def test_create_item_zero_price_raises(self):
        with pytest.raises(ValidationException, match="price must be greater than zero"):
            MenuItem.create(
                menu_id=uuid.uuid4(),
                restaurant_id=uuid.uuid4(),
                name="Free Item",
                price=Money(amount=Decimal("0")),
            )

    def test_update_item_details(self):
        item = MenuItem.create(
            menu_id=uuid.uuid4(),
            restaurant_id=uuid.uuid4(),
            name="Old Name",
            price=self._make_price(),
        )
        item.collect_events()

        new_price = Money(amount=Decimal("15.00"))
        item.update_details(name="New Name", price=new_price, dietary_labels=["vegan"])

        assert item.name == "New Name"
        assert item.price.amount == Decimal("15.00")
        assert item.dietary_labels == ["vegan"]

    def test_set_availability(self):
        item = MenuItem.create(
            menu_id=uuid.uuid4(),
            restaurant_id=uuid.uuid4(),
            name="Soup",
            price=self._make_price(),
        )
        item.collect_events()

        item.set_availability(False)
        assert item.is_available is False

    def test_change_price(self):
        item = MenuItem.create(
            menu_id=uuid.uuid4(),
            restaurant_id=uuid.uuid4(),
            name="Salad",
            price=self._make_price("8.00"),
        )
        item.collect_events()

        item.change_price(Decimal("10.00"))
        assert item.price.amount == Decimal("10.00")
        assert item.price.currency == "USD"

    def test_mark_removed(self):
        item = MenuItem.create(
            menu_id=uuid.uuid4(),
            restaurant_id=uuid.uuid4(),
            name="Old Dish",
            price=self._make_price(),
        )
        item.collect_events()

        item.mark_removed()
        assert item.is_available is False
        events = item.collect_events()
        assert any(e.__class__.__name__ == "MenuItemRemoved" for e in events)
