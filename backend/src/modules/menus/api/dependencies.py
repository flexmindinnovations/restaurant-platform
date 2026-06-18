from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db_session
from modules.menus.application.commands.create_menu import CreateMenuHandler
from modules.menus.application.commands.delete_menu import DeleteMenuHandler
from modules.menus.application.commands.manage_categories import (
    AddCategoryHandler,
    DeleteCategoryHandler,
    UpdateCategoryHandler,
)
from modules.menus.application.commands.manage_items import (
    CreateMenuItemHandler,
    DeleteMenuItemHandler,
    UpdateMenuItemHandler,
)
from modules.menus.application.commands.update_menu import UpdateMenuHandler
from modules.menus.application.queries.get_menu import GetMenuHandler
from modules.menus.application.queries.get_menu_item import GetMenuItemHandler
from modules.menus.application.queries.list_menu_items import ListMenuItemsHandler
from modules.menus.application.queries.list_menus import ListMenusHandler
from modules.menus.infrastructure.repositories.category_repository import SqlAlchemyCategoryRepository
from modules.menus.infrastructure.repositories.menu_item_repository import SqlAlchemyMenuItemRepository
from modules.menus.infrastructure.repositories.menu_repository import SqlAlchemyMenuRepository
from shared.infrastructure.event_bus import get_event_bus
from shared.infrastructure.unit_of_work import SqlAlchemyUnitOfWork


def _menu_repo(session: AsyncSession = Depends(get_db_session)) -> SqlAlchemyMenuRepository:
    return SqlAlchemyMenuRepository(session)


def _category_repo(session: AsyncSession = Depends(get_db_session)) -> SqlAlchemyCategoryRepository:
    return SqlAlchemyCategoryRepository(session)


def _item_repo(session: AsyncSession = Depends(get_db_session)) -> SqlAlchemyMenuItemRepository:
    return SqlAlchemyMenuItemRepository(session)


def _uow(session: AsyncSession = Depends(get_db_session)) -> SqlAlchemyUnitOfWork:
    return SqlAlchemyUnitOfWork(session, get_event_bus())


def get_create_menu_handler(
    menu_repo: SqlAlchemyMenuRepository = Depends(_menu_repo),
    uow: SqlAlchemyUnitOfWork = Depends(_uow),
) -> CreateMenuHandler:
    return CreateMenuHandler(menu_repo, uow)


def get_update_menu_handler(
    menu_repo: SqlAlchemyMenuRepository = Depends(_menu_repo),
    uow: SqlAlchemyUnitOfWork = Depends(_uow),
) -> UpdateMenuHandler:
    return UpdateMenuHandler(menu_repo, uow)


def get_delete_menu_handler(
    menu_repo: SqlAlchemyMenuRepository = Depends(_menu_repo),
    uow: SqlAlchemyUnitOfWork = Depends(_uow),
) -> DeleteMenuHandler:
    return DeleteMenuHandler(menu_repo, uow)


def get_menu_query_handler(
    menu_repo: SqlAlchemyMenuRepository = Depends(_menu_repo),
    category_repo: SqlAlchemyCategoryRepository = Depends(_category_repo),
) -> GetMenuHandler:
    return GetMenuHandler(menu_repo, category_repo)


def get_list_menus_handler(
    menu_repo: SqlAlchemyMenuRepository = Depends(_menu_repo),
) -> ListMenusHandler:
    return ListMenusHandler(menu_repo)


def get_add_category_handler(
    menu_repo: SqlAlchemyMenuRepository = Depends(_menu_repo),
    category_repo: SqlAlchemyCategoryRepository = Depends(_category_repo),
    uow: SqlAlchemyUnitOfWork = Depends(_uow),
) -> AddCategoryHandler:
    return AddCategoryHandler(menu_repo, category_repo, uow)


def get_update_category_handler(
    category_repo: SqlAlchemyCategoryRepository = Depends(_category_repo),
    uow: SqlAlchemyUnitOfWork = Depends(_uow),
) -> UpdateCategoryHandler:
    return UpdateCategoryHandler(category_repo, uow)


def get_delete_category_handler(
    category_repo: SqlAlchemyCategoryRepository = Depends(_category_repo),
    uow: SqlAlchemyUnitOfWork = Depends(_uow),
) -> DeleteCategoryHandler:
    return DeleteCategoryHandler(category_repo, uow)


def get_create_item_handler(
    menu_repo: SqlAlchemyMenuRepository = Depends(_menu_repo),
    item_repo: SqlAlchemyMenuItemRepository = Depends(_item_repo),
    uow: SqlAlchemyUnitOfWork = Depends(_uow),
) -> CreateMenuItemHandler:
    return CreateMenuItemHandler(menu_repo, item_repo, uow)


def get_update_item_handler(
    item_repo: SqlAlchemyMenuItemRepository = Depends(_item_repo),
    uow: SqlAlchemyUnitOfWork = Depends(_uow),
) -> UpdateMenuItemHandler:
    return UpdateMenuItemHandler(item_repo, uow)


def get_delete_item_handler(
    item_repo: SqlAlchemyMenuItemRepository = Depends(_item_repo),
    uow: SqlAlchemyUnitOfWork = Depends(_uow),
) -> DeleteMenuItemHandler:
    return DeleteMenuItemHandler(item_repo, uow)


def get_item_query_handler(
    item_repo: SqlAlchemyMenuItemRepository = Depends(_item_repo),
) -> GetMenuItemHandler:
    return GetMenuItemHandler(item_repo)


def get_list_items_handler(
    item_repo: SqlAlchemyMenuItemRepository = Depends(_item_repo),
) -> ListMenuItemsHandler:
    return ListMenuItemsHandler(item_repo)
