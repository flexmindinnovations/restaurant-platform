import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from modules.restaurants.application.commands.register_restaurant import (
    RegisterRestaurantCommand,
    RegisterRestaurantHandler,
)
from modules.restaurants.application.commands.update_restaurant import (
    UpdateRestaurantCommand,
    UpdateRestaurantHandler,
)
from modules.restaurants.application.commands.verify_restaurant import (
    VerifyRestaurantCommand,
    VerifyRestaurantHandler,
)
from modules.restaurants.application.queries.get_restaurant import GetRestaurantHandler, GetRestaurantQuery
from modules.restaurants.application.queries.list_restaurants import (
    ListRestaurantsHandler,
    ListRestaurantsQuery,
)
from modules.restaurants.domain.entities.restaurant import Restaurant
from modules.restaurants.domain.value_objects.operating_hours import OperatingHours
from shared.domain.exceptions import NotFoundException
from shared.domain.value_objects import Address


def _make_restaurant(
    *,
    owner_id: uuid.UUID | None = None,
    name: str = "Test Restaurant",
    active: bool = True,
    verified: bool = False,
) -> Restaurant:
    return Restaurant(
        id=uuid.uuid4(),
        owner_id=owner_id or uuid.uuid4(),
        name=name,
        description="A test restaurant",
        cuisine_types=["Italian"],
        address=Address("1 Main St", "City", "ST", "12345", "US"),
        phone="+1234567890",
        email="test@restaurant.com",
        operating_hours=OperatingHours({"monday": {"open": "09:00", "close": "22:00"}}),
        is_active=active,
        is_verified=verified,
        rating_avg=0.0,
        total_reviews=0,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


def _mock_uow() -> AsyncMock:
    uow = AsyncMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)
    uow._aggregates = []
    uow.register_aggregate = MagicMock(side_effect=lambda agg: uow._aggregates.append(agg))
    return uow


def _mock_repo() -> AsyncMock:
    return AsyncMock()


_VALID_SCHEDULE = {"monday": {"open": "09:00", "close": "22:00"}}


# ---------------------------------------------------------------------------
# RegisterRestaurantHandler
# ---------------------------------------------------------------------------


class TestRegisterRestaurantHandler:
    @pytest.mark.asyncio
    async def test_register_restaurant_success(self) -> None:
        repo = _mock_repo()
        uow = _mock_uow()

        handler = RegisterRestaurantHandler(repo, uow)
        cmd = RegisterRestaurantCommand(
            owner_id=uuid.uuid4(),
            name="Taco Palace",
            phone="+1234567890",
            email="info@taco.com",
            address_street="123 Main",
            address_city="Springfield",
            address_state="IL",
            address_postal_code="62701",
            address_country="US",
            operating_hours=_VALID_SCHEDULE,
        )

        result = await handler.handle(cmd)

        assert isinstance(result, uuid.UUID)
        repo.add.assert_awaited_once()
        uow.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_register_restaurant_with_optional_fields(self) -> None:
        repo = _mock_repo()
        uow = _mock_uow()

        handler = RegisterRestaurantHandler(repo, uow)
        cmd = RegisterRestaurantCommand(
            owner_id=uuid.uuid4(),
            name="Sushi Place",
            phone="+9876543210",
            email="sushi@place.com",
            address_street="456 Oak",
            address_city="Portland",
            address_state="OR",
            address_postal_code="97201",
            address_country="US",
            operating_hours=_VALID_SCHEDULE,
            description="Best sushi in town",
            cuisine_types=["Japanese", "Sushi"],
            address_latitude=45.5,
            address_longitude=-122.6,
        )

        result = await handler.handle(cmd)
        assert isinstance(result, uuid.UUID)
        added = repo.add.call_args[0][0]
        assert added.description == "Best sushi in town"
        assert added.cuisine_types == ["Japanese", "Sushi"]
        assert added.address.latitude == 45.5


# ---------------------------------------------------------------------------
# UpdateRestaurantHandler
# ---------------------------------------------------------------------------


class TestUpdateRestaurantHandler:
    @pytest.mark.asyncio
    async def test_update_restaurant_name(self) -> None:
        restaurant = _make_restaurant()
        repo = _mock_repo()
        repo.get_by_id.return_value = restaurant
        uow = _mock_uow()

        handler = UpdateRestaurantHandler(repo, uow)
        await handler.handle(
            UpdateRestaurantCommand(
                restaurant_id=restaurant.id,
                name="Updated Name",
            )
        )

        assert restaurant.name == "Updated Name"
        repo.update.assert_awaited_once()
        uow.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_update_restaurant_not_found(self) -> None:
        repo = _mock_repo()
        repo.get_by_id.return_value = None
        uow = _mock_uow()

        handler = UpdateRestaurantHandler(repo, uow)

        with pytest.raises(NotFoundException, match="Restaurant not found"):
            await handler.handle(UpdateRestaurantCommand(restaurant_id=uuid.uuid4(), name="X"))

    @pytest.mark.asyncio
    async def test_update_restaurant_address(self) -> None:
        restaurant = _make_restaurant()
        repo = _mock_repo()
        repo.get_by_id.return_value = restaurant
        uow = _mock_uow()

        handler = UpdateRestaurantHandler(repo, uow)
        await handler.handle(
            UpdateRestaurantCommand(
                restaurant_id=restaurant.id,
                address_street="999 New St",
                address_city="NewCity",
            )
        )

        assert restaurant.address.street == "999 New St"
        assert restaurant.address.city == "NewCity"
        assert restaurant.address.state == "ST"

    @pytest.mark.asyncio
    async def test_update_deactivated_restaurant_raises(self) -> None:
        restaurant = _make_restaurant(active=False)
        repo = _mock_repo()
        repo.get_by_id.return_value = restaurant
        uow = _mock_uow()

        handler = UpdateRestaurantHandler(repo, uow)

        from shared.domain.exceptions import ValidationException

        with pytest.raises(ValidationException):
            await handler.handle(
                UpdateRestaurantCommand(
                    restaurant_id=restaurant.id,
                    name="Should Fail",
                )
            )


# ---------------------------------------------------------------------------
# VerifyRestaurantHandler
# ---------------------------------------------------------------------------


class TestVerifyRestaurantHandler:
    @pytest.mark.asyncio
    async def test_verify_restaurant_success(self) -> None:
        restaurant = _make_restaurant(verified=False)
        repo = _mock_repo()
        repo.get_by_id.return_value = restaurant
        uow = _mock_uow()

        handler = VerifyRestaurantHandler(repo, uow)
        await handler.handle(VerifyRestaurantCommand(restaurant_id=restaurant.id))

        assert restaurant.is_verified is True
        repo.update.assert_awaited_once()
        uow.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_verify_restaurant_not_found(self) -> None:
        repo = _mock_repo()
        repo.get_by_id.return_value = None
        uow = _mock_uow()

        handler = VerifyRestaurantHandler(repo, uow)

        with pytest.raises(NotFoundException, match="Restaurant not found"):
            await handler.handle(VerifyRestaurantCommand(restaurant_id=uuid.uuid4()))


# ---------------------------------------------------------------------------
# GetRestaurantHandler
# ---------------------------------------------------------------------------


class TestGetRestaurantHandler:
    @pytest.mark.asyncio
    async def test_get_restaurant_success(self) -> None:
        restaurant = _make_restaurant(name="My Place")
        repo = _mock_repo()
        repo.get_by_id.return_value = restaurant

        handler = GetRestaurantHandler(repo)
        result = await handler.handle(GetRestaurantQuery(restaurant_id=restaurant.id))

        assert result.name == "My Place"
        assert result.id == restaurant.id

    @pytest.mark.asyncio
    async def test_get_restaurant_not_found(self) -> None:
        repo = _mock_repo()
        repo.get_by_id.return_value = None

        handler = GetRestaurantHandler(repo)

        with pytest.raises(NotFoundException, match="Restaurant not found"):
            await handler.handle(GetRestaurantQuery(restaurant_id=uuid.uuid4()))


# ---------------------------------------------------------------------------
# ListRestaurantsHandler
# ---------------------------------------------------------------------------


class TestListRestaurantsHandler:
    @pytest.mark.asyncio
    async def test_list_restaurants_success(self) -> None:
        restaurants = [_make_restaurant(name="A"), _make_restaurant(name="B")]
        repo = _mock_repo()
        repo.list_all.return_value = restaurants
        repo.count_all.return_value = 2

        handler = ListRestaurantsHandler(repo)
        result = await handler.handle(ListRestaurantsQuery(skip=0, limit=10))

        assert result.total == 2
        assert len(result.items) == 2
        assert result.items[0].name == "A"

    @pytest.mark.asyncio
    async def test_list_restaurants_empty(self) -> None:
        repo = _mock_repo()
        repo.list_all.return_value = []
        repo.count_all.return_value = 0

        handler = ListRestaurantsHandler(repo)
        result = await handler.handle(ListRestaurantsQuery())

        assert result.total == 0
        assert result.items == []

    @pytest.mark.asyncio
    async def test_list_restaurants_with_search(self) -> None:
        repo = _mock_repo()
        repo.list_all.return_value = [_make_restaurant(name="Taco Palace")]
        repo.count_all.return_value = 1

        handler = ListRestaurantsHandler(repo)
        result = await handler.handle(ListRestaurantsQuery(search="taco"))

        repo.list_all.assert_awaited_once_with(skip=0, limit=10, search="taco")
        repo.count_all.assert_awaited_once_with(search="taco")
        assert result.total == 1
