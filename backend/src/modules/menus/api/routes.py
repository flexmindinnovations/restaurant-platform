import uuid
from typing import Any

from fastapi import APIRouter, Depends, Query, status

from modules.menus.api.dependencies import (
    get_add_category_handler,
    get_create_item_handler,
    get_create_menu_handler,
    get_delete_category_handler,
    get_delete_item_handler,
    get_delete_menu_handler,
    get_item_query_handler,
    get_list_items_handler,
    get_list_menus_handler,
    get_menu_query_handler,
    get_update_category_handler,
    get_update_item_handler,
    get_update_menu_handler,
)
from modules.menus.api.schemas import (
    CategoryRequest,
    CategoryResponse,
    CreateMenuItemRequest,
    CreateMenuRequest,
    MenuItemListResponse,
    MenuItemResponse,
    MenuListResponse,
    MenuResponse,
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
from modules.menus.application.commands.update_menu import UpdateMenuCommand, UpdateMenuHandler
from modules.menus.application.queries.get_menu import GetMenuHandler, GetMenuQuery
from modules.menus.application.queries.get_menu_item import GetMenuItemHandler, GetMenuItemQuery
from modules.menus.application.queries.list_menu_items import ListMenuItemsHandler, ListMenuItemsQuery
from modules.menus.application.queries.list_menus import ListMenusHandler, ListMenusQuery
from shared.api.response import ResponseEnvelope
from shared.api.security import require_roles

router = APIRouter()


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
