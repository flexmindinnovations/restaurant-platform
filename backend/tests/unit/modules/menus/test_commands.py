import uuid
from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from modules.menus.application.commands.create_menu import CreateMenuCommand, CreateMenuHandler
from modules.menus.application.commands.delete_menu import DeleteMenuCommand, DeleteMenuHandler
from modules.menus.application.commands.manage_categories import (
    AddCategoryCommand,
    AddCategoryHandler,
    DeleteCategoryCommand,
    DeleteCategoryHandler,
    UpdateCategoryCommand,
    UpdateCategoryHandler,
)
from modules.menus.application.commands.manage_items import (
    CreateMenuItemCommand,
    CreateMenuItemHandler,
    DeleteMenuItemCommand,
    DeleteMenuItemHandler,
    UpdateMenuItemCommand,
    UpdateMenuItemHandler,
)
from modules.menus.application.commands.update_menu import UpdateMenuCommand, UpdateMenuHandler
from modules.menus.application.queries.get_menu import GetMenuHandler, GetMenuQuery
from modules.menus.application.queries.get_menu_item import GetMenuItemHandler, GetMenuItemQuery
from modules.menus.application.queries.list_menu_items import ListMenuItemsHandler, ListMenuItemsQuery
from modules.menus.application.queries.list_menus import ListMenusHandler, ListMenusQuery
from modules.menus.application.queries.search_menu_items import SearchMenuItemsHandler, SearchMenuItemsQuery
from modules.menus.domain.entities.category import Category
from modules.menus.domain.entities.menu import Menu
from modules.menus.domain.entities.menu_item import MenuItem
from shared.domain.exceptions import NotFoundException
from shared.domain.value_objects import Money


def _mock_uow() -> AsyncMock:
    uow = AsyncMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)
    uow._aggregates = []
    uow.register_aggregate = MagicMock(side_effect=lambda agg: uow._aggregates.append(agg))
    return uow


def _make_menu(
    *,
    restaurant_id: uuid.UUID | None = None,
    name: str = "Test Menu",
    is_active: bool = False,
) -> Menu:
    return Menu(
        id=uuid.uuid4(),
        restaurant_id=restaurant_id or uuid.uuid4(),
        name=name,
        description=None,
        is_active=is_active,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


def _make_category(*, menu_id: uuid.UUID | None = None, name: str = "Starters") -> Category:
    return Category(
        id=uuid.uuid4(),
        menu_id=menu_id or uuid.uuid4(),
        name=name,
        description=None,
        display_order=0,
        is_active=True,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


def _make_item(
    *,
    menu_id: uuid.UUID | None = None,
    restaurant_id: uuid.UUID | None = None,
    name: str = "Burger",
    price_amount: str = "12.00",
) -> MenuItem:
    return MenuItem(
        id=uuid.uuid4(),
        menu_id=menu_id or uuid.uuid4(),
        category_id=None,
        restaurant_id=restaurant_id or uuid.uuid4(),
        name=name,
        description=None,
        price=Money(amount=Decimal(price_amount)),
        image_url=None,
        display_order=0,
        is_available=True,
        dietary_labels=[],
        preparation_time_minutes=None,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


# ---------------------------------------------------------------------------
# Menu handlers
# ---------------------------------------------------------------------------


class TestCreateMenuHandler:
    @pytest.mark.asyncio
    async def test_create_menu_success(self):
        repo = AsyncMock()
        uow = _mock_uow()

        handler = CreateMenuHandler(repo, uow)
        result = await handler.handle(
            CreateMenuCommand(restaurant_id=uuid.uuid4(), name="Dinner")
        )

        assert isinstance(result, uuid.UUID)
        repo.add.assert_awaited_once()
        uow.commit.assert_awaited_once()


class TestUpdateMenuHandler:
    @pytest.mark.asyncio
    async def test_update_menu_success(self):
        menu = _make_menu()
        repo = AsyncMock()
        repo.get_by_id.return_value = menu
        uow = _mock_uow()

        handler = UpdateMenuHandler(repo, uow)
        await handler.handle(UpdateMenuCommand(menu_id=menu.id, name="Updated"))

        assert menu.name == "Updated"
        repo.update.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_update_menu_not_found(self):
        repo = AsyncMock()
        repo.get_by_id.return_value = None
        uow = _mock_uow()

        handler = UpdateMenuHandler(repo, uow)
        with pytest.raises(NotFoundException, match="Menu not found"):
            await handler.handle(UpdateMenuCommand(menu_id=uuid.uuid4(), name="X"))

    @pytest.mark.asyncio
    async def test_update_menu_publish(self):
        menu = _make_menu(is_active=False)
        repo = AsyncMock()
        repo.get_by_id.return_value = menu
        uow = _mock_uow()

        handler = UpdateMenuHandler(repo, uow)
        await handler.handle(UpdateMenuCommand(menu_id=menu.id, is_active=True))

        assert menu.is_active is True


class TestDeleteMenuHandler:
    @pytest.mark.asyncio
    async def test_delete_menu_success(self):
        menu = _make_menu()
        repo = AsyncMock()
        repo.get_by_id.return_value = menu
        uow = _mock_uow()

        handler = DeleteMenuHandler(repo, uow)
        await handler.handle(DeleteMenuCommand(menu_id=menu.id))

        repo.delete.assert_awaited_once_with(menu.id)

    @pytest.mark.asyncio
    async def test_delete_menu_not_found(self):
        repo = AsyncMock()
        repo.get_by_id.return_value = None
        uow = _mock_uow()

        handler = DeleteMenuHandler(repo, uow)
        with pytest.raises(NotFoundException):
            await handler.handle(DeleteMenuCommand(menu_id=uuid.uuid4()))


# ---------------------------------------------------------------------------
# Category handlers
# ---------------------------------------------------------------------------


class TestAddCategoryHandler:
    @pytest.mark.asyncio
    async def test_add_category_success(self):
        menu = _make_menu()
        menu_repo = AsyncMock()
        menu_repo.get_by_id.return_value = menu
        category_repo = AsyncMock()
        uow = _mock_uow()

        handler = AddCategoryHandler(menu_repo, category_repo, uow)
        result = await handler.handle(
            AddCategoryCommand(menu_id=menu.id, name="Desserts")
        )

        assert isinstance(result, uuid.UUID)
        category_repo.add.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_add_category_menu_not_found(self):
        menu_repo = AsyncMock()
        menu_repo.get_by_id.return_value = None
        category_repo = AsyncMock()
        uow = _mock_uow()

        handler = AddCategoryHandler(menu_repo, category_repo, uow)
        with pytest.raises(NotFoundException, match="Menu not found"):
            await handler.handle(AddCategoryCommand(menu_id=uuid.uuid4(), name="X"))


class TestUpdateCategoryHandler:
    @pytest.mark.asyncio
    async def test_update_category_success(self):
        category = _make_category()
        repo = AsyncMock()
        repo.get_by_id.return_value = category
        uow = _mock_uow()

        handler = UpdateCategoryHandler(repo, uow)
        await handler.handle(
            UpdateCategoryCommand(category_id=category.id, name="Mains")
        )

        assert category.name == "Mains"
        repo.update.assert_awaited_once()


class TestDeleteCategoryHandler:
    @pytest.mark.asyncio
    async def test_delete_category_success(self):
        category = _make_category()
        repo = AsyncMock()
        repo.get_by_id.return_value = category
        uow = _mock_uow()

        handler = DeleteCategoryHandler(repo, uow)
        await handler.handle(DeleteCategoryCommand(category_id=category.id))

        repo.delete.assert_awaited_once_with(category.id)


# ---------------------------------------------------------------------------
# MenuItem handlers
# ---------------------------------------------------------------------------


class TestCreateMenuItemHandler:
    @pytest.mark.asyncio
    async def test_create_item_success(self):
        menu = _make_menu()
        menu_repo = AsyncMock()
        menu_repo.get_by_id.return_value = menu
        item_repo = AsyncMock()
        uow = _mock_uow()

        handler = CreateMenuItemHandler(menu_repo, item_repo, uow)
        result = await handler.handle(
            CreateMenuItemCommand(
                menu_id=menu.id,
                restaurant_id=menu.restaurant_id,
                name="Pizza",
                price_amount=Decimal("14.99"),
            )
        )

        assert isinstance(result, uuid.UUID)
        item_repo.add.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_create_item_menu_not_found(self):
        menu_repo = AsyncMock()
        menu_repo.get_by_id.return_value = None
        item_repo = AsyncMock()
        uow = _mock_uow()

        handler = CreateMenuItemHandler(menu_repo, item_repo, uow)
        with pytest.raises(NotFoundException, match="Menu not found"):
            await handler.handle(
                CreateMenuItemCommand(
                    menu_id=uuid.uuid4(),
                    restaurant_id=uuid.uuid4(),
                    name="Pizza",
                    price_amount=Decimal("14.99"),
                )
            )


class TestUpdateMenuItemHandler:
    @pytest.mark.asyncio
    async def test_update_item_success(self):
        item = _make_item()
        repo = AsyncMock()
        repo.get_by_id.return_value = item
        uow = _mock_uow()

        handler = UpdateMenuItemHandler(repo, uow)
        await handler.handle(
            UpdateMenuItemCommand(item_id=item.id, name="Deluxe Burger")
        )

        assert item.name == "Deluxe Burger"
        repo.update.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_update_item_not_found(self):
        repo = AsyncMock()
        repo.get_by_id.return_value = None
        uow = _mock_uow()

        handler = UpdateMenuItemHandler(repo, uow)
        with pytest.raises(NotFoundException, match="Menu item not found"):
            await handler.handle(
                UpdateMenuItemCommand(item_id=uuid.uuid4(), name="X")
            )

    @pytest.mark.asyncio
    async def test_update_item_price(self):
        item = _make_item(price_amount="10.00")
        repo = AsyncMock()
        repo.get_by_id.return_value = item
        uow = _mock_uow()

        handler = UpdateMenuItemHandler(repo, uow)
        await handler.handle(
            UpdateMenuItemCommand(item_id=item.id, price_amount=Decimal("15.50"))
        )

        assert item.price.amount == Decimal("15.50")


class TestDeleteMenuItemHandler:
    @pytest.mark.asyncio
    async def test_delete_item_success(self):
        item = _make_item()
        repo = AsyncMock()
        repo.get_by_id.return_value = item
        uow = _mock_uow()

        handler = DeleteMenuItemHandler(repo, uow)
        await handler.handle(DeleteMenuItemCommand(item_id=item.id))

        repo.delete.assert_awaited_once_with(item.id)


# ---------------------------------------------------------------------------
# Query handlers
# ---------------------------------------------------------------------------


class TestGetMenuHandler:
    @pytest.mark.asyncio
    async def test_get_menu_success(self):
        menu = _make_menu(name="Brunch")
        menu_repo = AsyncMock()
        menu_repo.get_by_id.return_value = menu
        category_repo = AsyncMock()
        category_repo.list_by_menu.return_value = []

        handler = GetMenuHandler(menu_repo, category_repo)
        result = await handler.handle(GetMenuQuery(menu_id=menu.id))

        assert result.name == "Brunch"
        assert result.categories == []

    @pytest.mark.asyncio
    async def test_get_menu_not_found(self):
        menu_repo = AsyncMock()
        menu_repo.get_by_id.return_value = None
        category_repo = AsyncMock()

        handler = GetMenuHandler(menu_repo, category_repo)
        with pytest.raises(NotFoundException):
            await handler.handle(GetMenuQuery(menu_id=uuid.uuid4()))


class TestListMenusHandler:
    @pytest.mark.asyncio
    async def test_list_menus_success(self):
        menus = [_make_menu(name="A"), _make_menu(name="B")]
        repo = AsyncMock()
        repo.list_by_restaurant.return_value = menus
        repo.count_by_restaurant.return_value = 2

        handler = ListMenusHandler(repo)
        result = await handler.handle(
            ListMenusQuery(restaurant_id=uuid.uuid4())
        )

        assert result.total == 2
        assert len(result.items) == 2

    @pytest.mark.asyncio
    async def test_list_menus_empty(self):
        repo = AsyncMock()
        repo.list_by_restaurant.return_value = []
        repo.count_by_restaurant.return_value = 0

        handler = ListMenusHandler(repo)
        result = await handler.handle(
            ListMenusQuery(restaurant_id=uuid.uuid4())
        )

        assert result.total == 0
        assert result.items == []


class TestGetMenuItemHandler:
    @pytest.mark.asyncio
    async def test_get_item_success(self):
        item = _make_item(name="Fries")
        repo = AsyncMock()
        repo.get_by_id.return_value = item

        handler = GetMenuItemHandler(repo)
        result = await handler.handle(GetMenuItemQuery(item_id=item.id))

        assert result.name == "Fries"
        assert result.price_amount == Decimal("12.00")

    @pytest.mark.asyncio
    async def test_get_item_not_found(self):
        repo = AsyncMock()
        repo.get_by_id.return_value = None

        handler = GetMenuItemHandler(repo)
        with pytest.raises(NotFoundException):
            await handler.handle(GetMenuItemQuery(item_id=uuid.uuid4()))


class TestListMenuItemsHandler:
    @pytest.mark.asyncio
    async def test_list_items_success(self):
        items = [_make_item(name="A"), _make_item(name="B")]
        repo = AsyncMock()
        repo.list_by_menu.return_value = items
        repo.count_by_menu.return_value = 2

        handler = ListMenuItemsHandler(repo)
        result = await handler.handle(
            ListMenuItemsQuery(menu_id=uuid.uuid4())
        )

        assert result.total == 2
        assert len(result.items) == 2


class TestSearchMenuItemsHandler:
    @pytest.mark.asyncio
    async def test_search_returns_results(self):
        restaurant_id = uuid.uuid4()
        items = [_make_item(name="Chicken Burger", restaurant_id=restaurant_id)]
        repo = AsyncMock()
        repo.search.return_value = items
        repo.search_count.return_value = 1

        handler = SearchMenuItemsHandler(repo)
        result = await handler.handle(
            SearchMenuItemsQuery(restaurant_id=restaurant_id, query="chicken")
        )

        assert result.total == 1
        assert result.items[0].name == "Chicken Burger"
        repo.search.assert_called_once_with(
            restaurant_id=restaurant_id,
            query="chicken",
            available_only=True,
            skip=0,
            limit=20,
        )

    @pytest.mark.asyncio
    async def test_search_empty_results(self):
        repo = AsyncMock()
        repo.search.return_value = []
        repo.search_count.return_value = 0

        handler = SearchMenuItemsHandler(repo)
        result = await handler.handle(
            SearchMenuItemsQuery(restaurant_id=uuid.uuid4(), query="nonexistent")
        )

        assert result.total == 0
        assert result.items == []
