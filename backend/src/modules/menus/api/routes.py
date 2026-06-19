import pathlib
import uuid
from typing import Any

from fastapi import APIRouter, Depends, Query, status

from app.dependencies import get_db_session
from modules.menus.api.dependencies import (
    get_add_category_handler,
    get_add_modifier_handler,
    get_create_item_handler,
    get_create_menu_handler,
    get_create_modifier_group_handler,
    get_delete_category_handler,
    get_delete_item_handler,
    get_delete_menu_handler,
    get_delete_modifier_group_handler,
    get_item_query_handler,
    get_list_items_handler,
    get_list_menus_handler,
    get_list_modifier_groups_handler,
    get_menu_query_handler,
    get_remove_modifier_handler,
    get_search_items_handler,
    get_update_category_handler,
    get_update_item_handler,
    get_update_menu_handler,
)
from modules.menus.api.schemas import (
    AddModifierRequest,
    CategoryRequest,
    CategoryResponse,
    CreateMenuItemRequest,
    CreateMenuRequest,
    CreateModifierGroupRequest,
    MenuItemListResponse,
    MenuItemResponse,
    MenuListResponse,
    MenuResponse,
    ModifierGroupResponse,
    UpdateCategoryRequest,
    UpdateMenuItemRequest,
    UpdateMenuRequest,
)
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
from modules.menus.application.commands.manage_modifiers import (
    AddModifierCommand,
    AddModifierHandler,
    CreateModifierGroupCommand,
    CreateModifierGroupHandler,
    DeleteModifierGroupCommand,
    DeleteModifierGroupHandler,
    RemoveModifierCommand,
    RemoveModifierHandler,
)
from modules.menus.application.commands.update_menu import UpdateMenuCommand, UpdateMenuHandler
from modules.menus.application.queries.get_menu import GetMenuHandler, GetMenuQuery
from modules.menus.application.queries.get_menu_item import GetMenuItemHandler, GetMenuItemQuery
from modules.menus.application.queries.list_menu_items import ListMenuItemsHandler, ListMenuItemsQuery
from modules.menus.application.queries.list_menus import ListMenusHandler, ListMenusQuery
from modules.menus.application.queries.list_modifier_groups import ListModifierGroupsHandler, ListModifierGroupsQuery
from modules.menus.application.queries.search_menu_items import SearchMenuItemsHandler, SearchMenuItemsQuery
from shared.api.response import ResponseEnvelope
from shared.api.security import require_roles

router = APIRouter()


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------


@router.get("/search", response_model=ResponseEnvelope[MenuItemListResponse])
async def search_menu_items(
    restaurant_id: uuid.UUID = Query(...),
    q: str = Query(..., min_length=1, max_length=200),
    available_only: bool = Query(True),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    handler: SearchMenuItemsHandler = Depends(get_search_items_handler),
) -> ResponseEnvelope[MenuItemListResponse]:
    query = SearchMenuItemsQuery(
        restaurant_id=restaurant_id,
        query=q,
        available_only=available_only,
        skip=skip,
        limit=limit,
    )
    result = await handler.handle(query)
    items = [MenuItemResponse.model_validate(i) for i in result.items]
    return ResponseEnvelope(data=MenuItemListResponse(items=items, total=result.total))


@router.get("/search/semantic", response_model=ResponseEnvelope[MenuItemListResponse])
async def semantic_search_menu_items(
    restaurant_id: uuid.UUID = Query(...),
    q: str = Query(..., min_length=1, max_length=200),
    available_only: bool = Query(True),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    session: Any = Depends(get_db_session),
    search_handler: SearchMenuItemsHandler = Depends(get_search_items_handler),
) -> ResponseEnvelope[MenuItemListResponse]:
    import sys

    import structlog

    ai_path = str((pathlib.Path(__file__).parent / "../../../../../ai/src").resolve())
    if ai_path not in sys.path:
        sys.path.append(ai_path)

    from gateway.client import GeminiClient

    try:
        client = GeminiClient()
        query_vector = await client.embed_content(q)
    except Exception as e:
        structlog.get_logger().warning("Failed to generate embedding for query, falling back to pg_trgm", error=str(e))
        return await search_menu_items(
            restaurant_id=restaurant_id,
            q=q,
            available_only=available_only,
            skip=skip,
            limit=limit,
            handler=search_handler,
        )

    from sqlalchemy import func, select

    from modules.menus.infrastructure.models.menu_models import MenuItemEmbeddingModel, MenuItemModel

    stmt = (
        select(MenuItemModel)
        .join(MenuItemEmbeddingModel, MenuItemModel.id == MenuItemEmbeddingModel.menu_item_id)
        .where(MenuItemModel.restaurant_id == restaurant_id)
    )
    if available_only:
        stmt = stmt.where(MenuItemModel.is_available.is_(True))

    distance_expr = MenuItemEmbeddingModel.embedding.op("<=>")(query_vector)
    stmt = stmt.order_by(distance_expr).offset(skip).limit(limit)

    try:
        result = await session.execute(stmt)
        items = result.scalars().all()
    except Exception as db_err:
        structlog.get_logger().warning(
            "Semantic search database query failed, falling back to pg_trgm", error=str(db_err)
        )
        return await search_menu_items(
            restaurant_id=restaurant_id,
            q=q,
            available_only=available_only,
            skip=skip,
            limit=limit,
            handler=search_handler,
        )

    if not items:
        return await search_menu_items(
            restaurant_id=restaurant_id,
            q=q,
            available_only=available_only,
            skip=skip,
            limit=limit,
            handler=search_handler,
        )

    count_stmt = (
        select(func.count(MenuItemModel.id))
        .join(MenuItemEmbeddingModel, MenuItemModel.id == MenuItemEmbeddingModel.menu_item_id)
        .where(MenuItemModel.restaurant_id == restaurant_id)
    )
    if available_only:
        count_stmt = count_stmt.where(MenuItemModel.is_available.is_(True))

    try:
        count_result = await session.execute(count_stmt)
        total = count_result.scalar_one()
    except Exception as db_err:
        structlog.get_logger().warning(
            "Semantic search database count query failed, falling back to pg_trgm", error=str(db_err)
        )
        return await search_menu_items(
            restaurant_id=restaurant_id,
            q=q,
            available_only=available_only,
            skip=skip,
            limit=limit,
            handler=search_handler,
        )

    dtos = [MenuItemResponse.model_validate(item) for item in items]
    return ResponseEnvelope(data=MenuItemListResponse(items=dtos, total=total))


# ---------------------------------------------------------------------------
# Menu CRUD
# ---------------------------------------------------------------------------


@router.post("", response_model=ResponseEnvelope[MenuResponse], status_code=status.HTTP_201_CREATED)
async def create_menu(
    request: CreateMenuRequest,
    current_user: dict[str, Any] = Depends(require_roles("RESTAURANT_OWNER", "SUPER_ADMIN")),
    handler: CreateMenuHandler = Depends(get_create_menu_handler),
    query_handler: GetMenuHandler = Depends(get_menu_query_handler),
) -> ResponseEnvelope[MenuResponse]:
    restaurant_id = uuid.UUID(current_user["restaurant_id"])
    command = CreateMenuCommand(
        restaurant_id=restaurant_id,
        name=request.name,
        description=request.description,
    )
    menu_id = await handler.handle(command)
    dto = await query_handler.handle(GetMenuQuery(menu_id=menu_id))
    return ResponseEnvelope(data=MenuResponse.model_validate(dto))


@router.get("", response_model=ResponseEnvelope[MenuListResponse])
async def list_menus(
    restaurant_id: uuid.UUID = Query(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    active_only: bool = Query(False),
    handler: ListMenusHandler = Depends(get_list_menus_handler),
) -> ResponseEnvelope[MenuListResponse]:
    query = ListMenusQuery(
        restaurant_id=restaurant_id,
        skip=skip,
        limit=limit,
        active_only=active_only,
    )
    result = await handler.handle(query)
    items = [MenuResponse.model_validate(m) for m in result.items]
    return ResponseEnvelope(data=MenuListResponse(items=items, total=result.total))


@router.get("/{menu_id}", response_model=ResponseEnvelope[MenuResponse])
async def get_menu(
    menu_id: uuid.UUID,
    handler: GetMenuHandler = Depends(get_menu_query_handler),
) -> ResponseEnvelope[MenuResponse]:
    dto = await handler.handle(GetMenuQuery(menu_id=menu_id))
    return ResponseEnvelope(data=MenuResponse.model_validate(dto))


@router.patch("/{menu_id}", response_model=ResponseEnvelope[dict])
async def update_menu(
    menu_id: uuid.UUID,
    request: UpdateMenuRequest,
    _current_user: dict[str, Any] = Depends(require_roles("RESTAURANT_OWNER", "SUPER_ADMIN")),
    handler: UpdateMenuHandler = Depends(get_update_menu_handler),
) -> ResponseEnvelope[dict]:
    command = UpdateMenuCommand(
        menu_id=menu_id,
        name=request.name,
        description=request.description,
        is_active=request.is_active,
    )
    await handler.handle(command)
    return ResponseEnvelope(data={"message": "Menu updated successfully"})


@router.delete("/{menu_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_menu(
    menu_id: uuid.UUID,
    _current_user: dict[str, Any] = Depends(require_roles("RESTAURANT_OWNER", "SUPER_ADMIN")),
    handler: DeleteMenuHandler = Depends(get_delete_menu_handler),
) -> None:
    await handler.handle(DeleteMenuCommand(menu_id=menu_id))


# ---------------------------------------------------------------------------
# Category management
# ---------------------------------------------------------------------------


@router.post(
    "/{menu_id}/categories",
    response_model=ResponseEnvelope[CategoryResponse],
    status_code=status.HTTP_201_CREATED,
)
async def add_category(
    menu_id: uuid.UUID,
    request: CategoryRequest,
    _current_user: dict[str, Any] = Depends(require_roles("RESTAURANT_OWNER", "SUPER_ADMIN")),
    handler: AddCategoryHandler = Depends(get_add_category_handler),
) -> ResponseEnvelope[CategoryResponse]:
    command = AddCategoryCommand(
        menu_id=menu_id,
        name=request.name,
        description=request.description,
        display_order=request.display_order,
    )
    category_id = await handler.handle(command)
    return ResponseEnvelope(
        data=CategoryResponse(
            id=category_id,
            menu_id=menu_id,
            name=request.name,
            description=request.description,
            display_order=request.display_order,
            is_active=True,
            created_at=None,
            updated_at=None,
        )
    )


@router.patch("/categories/{category_id}", response_model=ResponseEnvelope[dict])
async def update_category(
    category_id: uuid.UUID,
    request: UpdateCategoryRequest,
    _current_user: dict[str, Any] = Depends(require_roles("RESTAURANT_OWNER", "SUPER_ADMIN")),
    handler: UpdateCategoryHandler = Depends(get_update_category_handler),
) -> ResponseEnvelope[dict]:
    command = UpdateCategoryCommand(
        category_id=category_id,
        name=request.name,
        description=request.description,
        display_order=request.display_order,
    )
    await handler.handle(command)
    return ResponseEnvelope(data={"message": "Category updated successfully"})


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: uuid.UUID,
    _current_user: dict[str, Any] = Depends(require_roles("RESTAURANT_OWNER", "SUPER_ADMIN")),
    handler: DeleteCategoryHandler = Depends(get_delete_category_handler),
) -> None:
    await handler.handle(DeleteCategoryCommand(category_id=category_id))


# ---------------------------------------------------------------------------
# Menu Item CRUD
# ---------------------------------------------------------------------------


@router.post(
    "/{menu_id}/items",
    response_model=ResponseEnvelope[MenuItemResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_menu_item(
    menu_id: uuid.UUID,
    request: CreateMenuItemRequest,
    current_user: dict[str, Any] = Depends(require_roles("RESTAURANT_OWNER", "SUPER_ADMIN")),
    handler: CreateMenuItemHandler = Depends(get_create_item_handler),
    query_handler: GetMenuItemHandler = Depends(get_item_query_handler),
) -> ResponseEnvelope[MenuItemResponse]:
    restaurant_id = uuid.UUID(current_user["restaurant_id"])
    command = CreateMenuItemCommand(
        menu_id=menu_id,
        restaurant_id=restaurant_id,
        name=request.name,
        price_amount=request.price_amount,
        price_currency=request.price_currency,
        category_id=request.category_id,
        description=request.description,
        image_url=request.image_url,
        display_order=request.display_order,
        dietary_labels=request.dietary_labels,
        preparation_time_minutes=request.preparation_time_minutes,
    )
    item_id = await handler.handle(command)
    dto = await query_handler.handle(GetMenuItemQuery(item_id=item_id))
    return ResponseEnvelope(data=MenuItemResponse.model_validate(dto))


@router.get("/{menu_id}/items", response_model=ResponseEnvelope[MenuItemListResponse])
async def list_menu_items(
    menu_id: uuid.UUID,
    category_id: uuid.UUID | None = Query(None),
    available_only: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    handler: ListMenuItemsHandler = Depends(get_list_items_handler),
) -> ResponseEnvelope[MenuItemListResponse]:
    query = ListMenuItemsQuery(
        menu_id=menu_id,
        category_id=category_id,
        available_only=available_only,
        skip=skip,
        limit=limit,
    )
    result = await handler.handle(query)
    items = [MenuItemResponse.model_validate(i) for i in result.items]
    return ResponseEnvelope(data=MenuItemListResponse(items=items, total=result.total))


@router.get("/items/{item_id}", response_model=ResponseEnvelope[MenuItemResponse])
async def get_menu_item(
    item_id: uuid.UUID,
    handler: GetMenuItemHandler = Depends(get_item_query_handler),
) -> ResponseEnvelope[MenuItemResponse]:
    dto = await handler.handle(GetMenuItemQuery(item_id=item_id))
    return ResponseEnvelope(data=MenuItemResponse.model_validate(dto))


@router.patch("/items/{item_id}", response_model=ResponseEnvelope[dict])
async def update_menu_item(
    item_id: uuid.UUID,
    request: UpdateMenuItemRequest,
    _current_user: dict[str, Any] = Depends(require_roles("RESTAURANT_OWNER", "SUPER_ADMIN")),
    handler: UpdateMenuItemHandler = Depends(get_update_item_handler),
) -> ResponseEnvelope[dict]:
    command = UpdateMenuItemCommand(
        item_id=item_id,
        name=request.name,
        description=request.description,
        price_amount=request.price_amount,
        price_currency=request.price_currency,
        category_id=request.category_id,
        image_url=request.image_url,
        display_order=request.display_order,
        is_available=request.is_available,
        dietary_labels=request.dietary_labels,
        preparation_time_minutes=request.preparation_time_minutes,
    )
    await handler.handle(command)
    return ResponseEnvelope(data={"message": "Menu item updated successfully"})


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_menu_item(
    item_id: uuid.UUID,
    _current_user: dict[str, Any] = Depends(require_roles("RESTAURANT_OWNER", "SUPER_ADMIN")),
    handler: DeleteMenuItemHandler = Depends(get_delete_item_handler),
) -> None:
    await handler.handle(DeleteMenuItemCommand(item_id=item_id))


# ---------------------------------------------------------------------------
# Modifier Groups & Modifiers
# ---------------------------------------------------------------------------


@router.get(
    "/items/{item_id}/modifier-groups",
    response_model=ResponseEnvelope[list[ModifierGroupResponse]],
)
async def list_modifier_groups(
    item_id: uuid.UUID,
    handler: ListModifierGroupsHandler = Depends(get_list_modifier_groups_handler),
) -> ResponseEnvelope[list[ModifierGroupResponse]]:
    dtos = await handler.handle(ListModifierGroupsQuery(menu_item_id=item_id))
    return ResponseEnvelope(data=[ModifierGroupResponse.model_validate(g) for g in dtos])


@router.post(
    "/items/{item_id}/modifier-groups",
    response_model=ResponseEnvelope[dict],
    status_code=status.HTTP_201_CREATED,
)
async def create_modifier_group(
    item_id: uuid.UUID,
    request: CreateModifierGroupRequest,
    current_user: dict[str, Any] = Depends(require_roles("RESTAURANT_OWNER", "SUPER_ADMIN")),
    handler: CreateModifierGroupHandler = Depends(get_create_modifier_group_handler),
) -> ResponseEnvelope[dict]:
    restaurant_id = uuid.UUID(current_user["restaurant_id"])
    command = CreateModifierGroupCommand(
        menu_item_id=item_id,
        restaurant_id=restaurant_id,
        name=request.name,
        selection_type=request.selection_type,
        min_selections=request.min_selections,
        max_selections=request.max_selections,
        is_required=request.is_required,
        description=request.description,
        display_order=request.display_order,
    )
    group_id = await handler.handle(command)
    return ResponseEnvelope(data={"id": str(group_id), "message": "Modifier group created"})


@router.delete("/modifier-groups/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_modifier_group(
    group_id: uuid.UUID,
    _current_user: dict[str, Any] = Depends(require_roles("RESTAURANT_OWNER", "SUPER_ADMIN")),
    handler: DeleteModifierGroupHandler = Depends(get_delete_modifier_group_handler),
) -> None:
    await handler.handle(DeleteModifierGroupCommand(modifier_group_id=group_id))


@router.post(
    "/modifier-groups/{group_id}/modifiers",
    response_model=ResponseEnvelope[dict],
    status_code=status.HTTP_201_CREATED,
)
async def add_modifier(
    group_id: uuid.UUID,
    request: AddModifierRequest,
    _current_user: dict[str, Any] = Depends(require_roles("RESTAURANT_OWNER", "SUPER_ADMIN")),
    handler: AddModifierHandler = Depends(get_add_modifier_handler),
) -> ResponseEnvelope[dict]:
    command = AddModifierCommand(
        modifier_group_id=group_id,
        name=request.name,
        price_adjustment_amount=request.price_adjustment_amount,
        price_adjustment_currency=request.price_adjustment_currency,
        is_default=request.is_default,
        display_order=request.display_order,
    )
    modifier_id = await handler.handle(command)
    return ResponseEnvelope(data={"id": str(modifier_id), "message": "Modifier added"})


@router.delete(
    "/modifier-groups/{group_id}/modifiers/{modifier_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_modifier(
    group_id: uuid.UUID,
    modifier_id: uuid.UUID,
    _current_user: dict[str, Any] = Depends(require_roles("RESTAURANT_OWNER", "SUPER_ADMIN")),
    handler: RemoveModifierHandler = Depends(get_remove_modifier_handler),
) -> None:
    await handler.handle(RemoveModifierCommand(modifier_group_id=group_id, modifier_id=modifier_id))
