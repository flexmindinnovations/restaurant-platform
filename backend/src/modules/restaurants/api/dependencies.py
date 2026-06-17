from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db_session
from modules.restaurants.application.commands.register_restaurant import RegisterRestaurantHandler
from modules.restaurants.application.commands.update_restaurant import UpdateRestaurantHandler
from modules.restaurants.application.commands.verify_restaurant import VerifyRestaurantHandler
from modules.restaurants.application.queries.get_restaurant import GetRestaurantHandler
from modules.restaurants.application.queries.list_restaurants import ListRestaurantsHandler
from modules.restaurants.infrastructure.repositories.restaurant_repository import SqlAlchemyRestaurantRepository
from shared.infrastructure.event_bus import get_event_bus
from shared.infrastructure.unit_of_work import SqlAlchemyUnitOfWork


def get_restaurant_repository(session: AsyncSession = Depends(get_db_session)) -> SqlAlchemyRestaurantRepository:
    return SqlAlchemyRestaurantRepository(session)


def get_uow(session: AsyncSession = Depends(get_db_session)) -> SqlAlchemyUnitOfWork:
    return SqlAlchemyUnitOfWork(session, get_event_bus())


def get_register_restaurant_handler(
    restaurant_repo: SqlAlchemyRestaurantRepository = Depends(get_restaurant_repository),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> RegisterRestaurantHandler:
    return RegisterRestaurantHandler(restaurant_repo, uow)


def get_update_restaurant_handler(
    restaurant_repo: SqlAlchemyRestaurantRepository = Depends(get_restaurant_repository),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> UpdateRestaurantHandler:
    return UpdateRestaurantHandler(restaurant_repo, uow)


def get_verify_restaurant_handler(
    restaurant_repo: SqlAlchemyRestaurantRepository = Depends(get_restaurant_repository),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> VerifyRestaurantHandler:
    return VerifyRestaurantHandler(restaurant_repo, uow)


def get_restaurant_query_handler(
    restaurant_repo: SqlAlchemyRestaurantRepository = Depends(get_restaurant_repository),
) -> GetRestaurantHandler:
    return GetRestaurantHandler(restaurant_repo)


def get_list_restaurants_query_handler(
    restaurant_repo: SqlAlchemyRestaurantRepository = Depends(get_restaurant_repository),
) -> ListRestaurantsHandler:
    return ListRestaurantsHandler(restaurant_repo)
