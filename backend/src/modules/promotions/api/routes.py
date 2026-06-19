import uuid
from typing import Any

from fastapi import APIRouter, Depends, Query, status

from modules.promotions.api.dependencies import (
    get_apply_promotion_handler,
    get_create_promotion_handler,
    get_deactivate_promotion_handler,
    get_list_promotions_handler,
    get_validate_promotion_handler,
)
from modules.promotions.api.schemas import (
    ApplyPromotionRequest,
    ApplyPromotionResponse,
    CreatePromotionRequest,
    PromotionListResponse,
    PromotionResponse,
    ValidatePromotionRequest,
    ValidatePromotionResponse,
)
from modules.promotions.application.commands.apply_promotion import ApplyPromotionCommand, ApplyPromotionHandler
from modules.promotions.application.commands.create_promotion import CreatePromotionCommand, CreatePromotionHandler
from modules.promotions.application.commands.deactivate_promotion import (
    DeactivatePromotionCommand,
    DeactivatePromotionHandler,
)
from modules.promotions.application.queries.list_promotions import ListPromotionsHandler, ListPromotionsQuery
from modules.promotions.application.queries.validate_promotion import (
    ValidatePromotionHandler,
    ValidatePromotionQuery,
)
from modules.promotions.domain.value_objects.promotion_type import PromotionType
from shared.api.response import ResponseEnvelope
from shared.api.security import get_current_user, require_roles

router = APIRouter()


def _promo_to_response(promo: Any) -> PromotionResponse:
    return PromotionResponse(
        id=promo.id,
        code=promo.code,
        description=promo.description,
        promotion_type=promo.promotion_type.value,
        value=promo.value,
        min_order_amount=promo.min_order_amount.amount if promo.min_order_amount else None,
        min_order_currency=promo.min_order_amount.currency if promo.min_order_amount else None,
        max_discount_amount=promo.max_discount.amount if promo.max_discount else None,
        max_discount_currency=promo.max_discount.currency if promo.max_discount else None,
        valid_from=promo.valid_from,
        valid_until=promo.valid_until,
        max_total_uses=promo.max_total_uses,
        max_uses_per_customer=promo.max_uses_per_customer,
        total_uses=promo.total_uses,
        status=promo.status.value,
        restaurant_id=promo.restaurant_id,
        is_valid=promo.is_valid,
        created_at=promo.created_at,
        updated_at=promo.updated_at,
    )


@router.post("", response_model=ResponseEnvelope[PromotionResponse], status_code=status.HTTP_201_CREATED)
async def create_promotion(
    request: CreatePromotionRequest,
    _current_user: dict[str, Any] = Depends(require_roles("SUPER_ADMIN", "RESTAURANT_OWNER")),
    handler: CreatePromotionHandler = Depends(get_create_promotion_handler),
    list_handler: ListPromotionsHandler = Depends(get_list_promotions_handler),
) -> ResponseEnvelope[PromotionResponse]:
    command = CreatePromotionCommand(
        code=request.code,
        description=request.description,
        promotion_type=PromotionType(request.promotion_type),
        value=request.value,
        valid_from=request.valid_from,
        valid_until=request.valid_until,
        min_order_amount=request.min_order_amount,
        max_discount_amount=request.max_discount_amount,
        currency=request.currency,
        max_total_uses=request.max_total_uses,
        max_uses_per_customer=request.max_uses_per_customer,
        restaurant_id=request.restaurant_id,
    )
    promo_id = await handler.handle(command)

    promos, _ = await list_handler.handle(ListPromotionsQuery(skip=0, limit=1))
    promo = next((p for p in promos if p.id == promo_id), promos[0] if promos else None)
    return ResponseEnvelope(data=_promo_to_response(promo))


@router.get("", response_model=ResponseEnvelope[PromotionListResponse])
async def list_promotions(
    available_only: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    _current_user: dict[str, Any] = Depends(get_current_user),
    handler: ListPromotionsHandler = Depends(get_list_promotions_handler),
) -> ResponseEnvelope[PromotionListResponse]:
    promos, total = await handler.handle(ListPromotionsQuery(available_only=available_only, skip=skip, limit=limit))
    items = [_promo_to_response(p) for p in promos]
    return ResponseEnvelope(data=PromotionListResponse(items=items, total=total))


@router.post("/validate", response_model=ResponseEnvelope[ValidatePromotionResponse])
async def validate_promotion(
    request: ValidatePromotionRequest,
    _current_user: dict[str, Any] = Depends(get_current_user),
    handler: ValidatePromotionHandler = Depends(get_validate_promotion_handler),
) -> ResponseEnvelope[ValidatePromotionResponse]:
    result = await handler.handle(
        ValidatePromotionQuery(code=request.code, order_amount=request.order_amount, currency=request.currency)
    )
    return ResponseEnvelope(
        data=ValidatePromotionResponse(
            is_valid=result.is_valid,
            discount_amount=result.discount_amount,
            discount_currency=result.discount_currency,
            promotion_type=result.promotion_type,
            description=result.description,
        )
    )


@router.post("/apply", response_model=ResponseEnvelope[ApplyPromotionResponse])
async def apply_promotion(
    request: ApplyPromotionRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    handler: ApplyPromotionHandler = Depends(get_apply_promotion_handler),
) -> ResponseEnvelope[ApplyPromotionResponse]:
    customer_id = uuid.UUID(current_user["sub"])
    order_id = uuid.uuid4()

    result = await handler.handle(
        ApplyPromotionCommand(
            code=request.code,
            order_id=order_id,
            customer_id=customer_id,
            order_amount=request.order_amount,
            currency=request.currency,
        )
    )
    return ResponseEnvelope(
        data=ApplyPromotionResponse(
            promotion_id=result.promotion_id,
            discount_amount=result.discount_amount,
            discount_currency=result.discount_currency,
        )
    )


@router.post("/{promotion_id}/deactivate", response_model=ResponseEnvelope[dict])
async def deactivate_promotion(
    promotion_id: uuid.UUID,
    _current_user: dict[str, Any] = Depends(require_roles("SUPER_ADMIN", "RESTAURANT_OWNER")),
    handler: DeactivatePromotionHandler = Depends(get_deactivate_promotion_handler),
) -> ResponseEnvelope[dict]:
    await handler.handle(DeactivatePromotionCommand(promotion_id=promotion_id))
    return ResponseEnvelope(data={"message": "Promotion deactivated successfully"})
