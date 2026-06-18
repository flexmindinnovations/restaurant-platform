from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.menu_service_adapter import MenuServiceAdapter
from app.dependencies import get_db_session, get_redis
from modules.orders.application.commands.add_to_cart import AddToCartHandler
from modules.orders.application.commands.cancel_order import CancelOrderHandler
from modules.orders.application.commands.clear_cart import ClearCartHandler
from modules.orders.application.commands.confirm_order import ConfirmOrderHandler
from modules.orders.application.commands.place_order import PlaceOrderHandler
from modules.orders.application.commands.remove_from_cart import RemoveFromCartHandler
from modules.orders.application.commands.update_cart_item import UpdateCartItemHandler
from modules.orders.application.commands.update_order_status import UpdateOrderStatusHandler
from modules.orders.application.ports.cart_repository import CartRepository
from modules.orders.application.ports.menu_service import MenuService
from modules.orders.application.ports.order_repository import OrderRepository
from modules.orders.application.queries.get_cart import GetCartHandler
from modules.orders.application.queries.get_order import GetOrderHandler
from modules.orders.application.queries.list_customer_orders import ListCustomerOrdersHandler
from modules.orders.application.queries.list_restaurant_orders import ListRestaurantOrdersHandler
from modules.orders.infrastructure.repositories.sqlalchemy_cart_repository import SqlAlchemyCartRepository
from modules.orders.infrastructure.repositories.sqlalchemy_order_repository import SqlAlchemyOrderRepository
from shared.application.ports.unit_of_work import AbstractUnitOfWork
from shared.infrastructure.event_bus import get_event_bus
from shared.infrastructure.unit_of_work import SqlAlchemyUnitOfWork

# --- Repository & Service Providers ---


def _cart_repo(
    session: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis),
) -> CartRepository:
    return SqlAlchemyCartRepository(session, redis)


def _order_repo(session: AsyncSession = Depends(get_db_session)) -> OrderRepository:
    return SqlAlchemyOrderRepository(session)


def _menu_service(session: AsyncSession = Depends(get_db_session)) -> MenuService:
    return MenuServiceAdapter(session)


def _uow(session: AsyncSession = Depends(get_db_session)) -> AbstractUnitOfWork:
    return SqlAlchemyUnitOfWork(session, get_event_bus())


# --- Command Handler Providers ---


def get_add_to_cart_handler(
    cart_repo: CartRepository = Depends(_cart_repo),
    menu_service: MenuService = Depends(_menu_service),
) -> AddToCartHandler:
    return AddToCartHandler(cart_repo, menu_service)


def get_update_cart_item_handler(
    cart_repo: CartRepository = Depends(_cart_repo),
) -> UpdateCartItemHandler:
    return UpdateCartItemHandler(cart_repo)


def get_remove_from_cart_handler(
    cart_repo: CartRepository = Depends(_cart_repo),
) -> RemoveFromCartHandler:
    return RemoveFromCartHandler(cart_repo)


def get_clear_cart_handler(
    cart_repo: CartRepository = Depends(_cart_repo),
) -> ClearCartHandler:
    return ClearCartHandler(cart_repo)


def get_place_order_handler(
    order_repo: OrderRepository = Depends(_order_repo),
    cart_repo: CartRepository = Depends(_cart_repo),
    uow: AbstractUnitOfWork = Depends(_uow),
) -> PlaceOrderHandler:
    return PlaceOrderHandler(order_repo, cart_repo, uow)


def get_confirm_order_handler(
    order_repo: OrderRepository = Depends(_order_repo),
    uow: AbstractUnitOfWork = Depends(_uow),
) -> ConfirmOrderHandler:
    return ConfirmOrderHandler(order_repo, uow)


def get_update_order_status_handler(
    order_repo: OrderRepository = Depends(_order_repo),
    uow: AbstractUnitOfWork = Depends(_uow),
) -> UpdateOrderStatusHandler:
    return UpdateOrderStatusHandler(order_repo, uow)


def get_cancel_order_handler(
    order_repo: OrderRepository = Depends(_order_repo),
    uow: AbstractUnitOfWork = Depends(_uow),
) -> CancelOrderHandler:
    return CancelOrderHandler(order_repo, uow)


# --- Query Handler Providers ---


def get_cart_query_handler(
    cart_repo: CartRepository = Depends(_cart_repo),
) -> GetCartHandler:
    return GetCartHandler(cart_repo)


def get_order_query_handler(
    order_repo: OrderRepository = Depends(_order_repo),
) -> GetOrderHandler:
    return GetOrderHandler(order_repo)


def get_list_customer_orders_handler(
    order_repo: OrderRepository = Depends(_order_repo),
) -> ListCustomerOrdersHandler:
    return ListCustomerOrdersHandler(order_repo)


def get_list_restaurant_orders_handler(
    order_repo: OrderRepository = Depends(_order_repo),
) -> ListRestaurantOrdersHandler:
    return ListRestaurantOrdersHandler(order_repo)
