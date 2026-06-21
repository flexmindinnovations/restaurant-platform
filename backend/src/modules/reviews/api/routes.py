import uuid
from typing import Any

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db_session
from modules.reviews.api.dependencies import (
    get_flag_review_handler,
    get_list_restaurant_reviews_handler,
    get_reply_to_review_handler,
    get_review_query_handler,
    get_review_summary_handler,
    get_submit_review_handler,
    get_update_review_handler,
)
from modules.reviews.api.schemas import (
    FlagReviewRequest,
    ReplyToReviewRequest,
    ReviewListResponse,
    ReviewResponse,
    ReviewSummaryResponse,
    SubmitReviewRequest,
    UpdateReviewRequest,
)
from modules.reviews.application.commands.flag_review import FlagReviewCommand, FlagReviewHandler
from modules.reviews.application.commands.reply_to_review import ReplyToReviewCommand, ReplyToReviewHandler
from modules.reviews.application.commands.submit_review import SubmitReviewCommand, SubmitReviewHandler
from modules.reviews.application.commands.update_review import UpdateReviewCommand, UpdateReviewHandler
from modules.reviews.application.queries.get_review import GetReviewHandler, GetReviewQuery
from modules.reviews.application.queries.get_review_summary import GetReviewSummaryHandler, GetReviewSummaryQuery
from modules.reviews.application.queries.list_restaurant_reviews import (
    ListRestaurantReviewsHandler,
    ListRestaurantReviewsQuery,
)
from shared.api.response import ResponseEnvelope
from shared.api.security import get_current_user, require_restaurant_access, require_roles

router = APIRouter()


def _review_to_response(review: Any) -> ReviewResponse:
    return ReviewResponse(
        id=review.id,
        order_id=review.order_id,
        customer_id=review.customer_id,
        restaurant_id=review.restaurant_id,
        rating=review.rating.value,
        comment=review.comment,
        sentiment=review.sentiment.value if review.sentiment else None,
        is_flagged=review.is_flagged,
        flag_reason=review.flag_reason,
        reply=review.reply,
        replied_at=review.replied_at,
        images=review.images,
        is_editable=review.is_editable,
        created_at=review.created_at,
        updated_at=review.updated_at,
    )


@router.post(
    "/orders/{order_id}",
    response_model=ResponseEnvelope[ReviewResponse],
    status_code=status.HTTP_201_CREATED,
)
async def submit_review(
    order_id: uuid.UUID,
    request: SubmitReviewRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    handler: SubmitReviewHandler = Depends(get_submit_review_handler),
    query_handler: GetReviewHandler = Depends(get_review_query_handler),
) -> ResponseEnvelope[ReviewResponse]:
    customer_id = uuid.UUID(current_user["sub"])
    command = SubmitReviewCommand(
        order_id=order_id,
        customer_id=customer_id,
        restaurant_id=request.restaurant_id,
        rating=request.rating,
        comment=request.comment,
        images=request.images,
    )
    review_id = await handler.handle(command)
    review = await query_handler.handle(GetReviewQuery(review_id=review_id))
    return ResponseEnvelope(data=_review_to_response(review))


@router.get("/{review_id}", response_model=ResponseEnvelope[ReviewResponse])
async def get_review(
    review_id: uuid.UUID,
    _current_user: dict[str, Any] = Depends(get_current_user),
    query_handler: GetReviewHandler = Depends(get_review_query_handler),
) -> ResponseEnvelope[ReviewResponse]:
    review = await query_handler.handle(GetReviewQuery(review_id=review_id))
    return ResponseEnvelope(data=_review_to_response(review))


@router.patch("/{review_id}", response_model=ResponseEnvelope[ReviewResponse])
async def update_review(
    review_id: uuid.UUID,
    request: UpdateReviewRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    handler: UpdateReviewHandler = Depends(get_update_review_handler),
    query_handler: GetReviewHandler = Depends(get_review_query_handler),
) -> ResponseEnvelope[ReviewResponse]:
    customer_id = uuid.UUID(current_user["sub"])
    command = UpdateReviewCommand(
        review_id=review_id,
        customer_id=customer_id,
        rating=request.rating,
        comment=request.comment,
    )
    await handler.handle(command)
    review = await query_handler.handle(GetReviewQuery(review_id=review_id))
    return ResponseEnvelope(data=_review_to_response(review))


@router.post("/{review_id}/reply", response_model=ResponseEnvelope[ReviewResponse])
async def reply_to_review(
    review_id: uuid.UUID,
    request: ReplyToReviewRequest,
    current_user: dict[str, Any] = Depends(require_roles("RESTAURANT_OWNER", "RESTAURANT_STAFF", "SUPER_ADMIN")),
    handler: ReplyToReviewHandler = Depends(get_reply_to_review_handler),
    query_handler: GetReviewHandler = Depends(get_review_query_handler),
    session: AsyncSession = Depends(get_db_session),
) -> ResponseEnvelope[ReviewResponse]:
    review = await query_handler.handle(GetReviewQuery(review_id=review_id))
    await require_restaurant_access(review.restaurant_id, current_user, session)

    command = ReplyToReviewCommand(review_id=review_id, reply=request.reply)
    await handler.handle(command)
    review = await query_handler.handle(GetReviewQuery(review_id=review_id))
    return ResponseEnvelope(data=_review_to_response(review))


@router.post("/{review_id}/flag", response_model=ResponseEnvelope[dict])
async def flag_review(
    review_id: uuid.UUID,
    request: FlagReviewRequest,
    _current_user: dict[str, Any] = Depends(get_current_user),
    handler: FlagReviewHandler = Depends(get_flag_review_handler),
) -> ResponseEnvelope[dict]:
    command = FlagReviewCommand(review_id=review_id, reason=request.reason)
    await handler.handle(command)
    return ResponseEnvelope(data={"message": "Review flagged successfully"})


@router.get(
    "/restaurants/{restaurant_id}",
    response_model=ResponseEnvelope[ReviewListResponse],
)
async def list_restaurant_reviews(
    restaurant_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    handler: ListRestaurantReviewsHandler = Depends(get_list_restaurant_reviews_handler),
) -> ResponseEnvelope[ReviewListResponse]:
    reviews, total = await handler.handle(
        ListRestaurantReviewsQuery(restaurant_id=restaurant_id, skip=skip, limit=limit)
    )
    items = [_review_to_response(r) for r in reviews]
    return ResponseEnvelope(data=ReviewListResponse(items=items, total=total))


@router.get(
    "/restaurants/{restaurant_id}/summary",
    response_model=ResponseEnvelope[ReviewSummaryResponse],
)
async def get_review_summary(
    restaurant_id: uuid.UUID,
    handler: GetReviewSummaryHandler = Depends(get_review_summary_handler),
) -> ResponseEnvelope[ReviewSummaryResponse]:
    summary = await handler.handle(GetReviewSummaryQuery(restaurant_id=restaurant_id))
    return ResponseEnvelope(data=ReviewSummaryResponse.model_validate(summary.__dict__))


from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db_session


@router.get("", response_model=ResponseEnvelope[ReviewListResponse])
async def list_all_reviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session),
    _current_user: dict[str, Any] = Depends(get_current_user),
) -> ResponseEnvelope[ReviewListResponse]:
    from modules.reviews.infrastructure.models.review_models import ReviewModel
    from modules.users.infrastructure.models.profile_model import ProfileModel

    query = select(ReviewModel, ProfileModel).outerjoin(
        ProfileModel, ReviewModel.customer_id == ProfileModel.account_id
    )
    result = await db.execute(query)
    rows = result.all()
    
    items = []
    for model, prof in rows:
        cust_name = f"{prof.first_name} {prof.last_name}" if prof else "Customer"
        status = 'FLAGGED' if model.is_flagged else 'APPROVED' # simplified map
        items.append(ReviewResponse(
            id=model.id,
            order_id=model.order_id,
            customer_id=model.customer_id,
            restaurant_id=model.restaurant_id,
            rating=model.rating,
            comment=model.comment,
            sentiment=model.sentiment,
            is_flagged=model.is_flagged,
            flag_reason=model.flag_reason,
            reply=model.reply,
            replied_at=model.replied_at,
            images=model.images or [],
            is_editable=False,
            created_at=model.created_at,
            updated_at=model.updated_at,
        ))
    
    total = len(items)
    paginated = items[skip:skip+limit]
    return ResponseEnvelope(data=ReviewListResponse(items=paginated, total=total))


@router.post("/{review_id}/approve", response_model=ResponseEnvelope[dict])
async def approve_review(
    review_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    _current_user: dict[str, Any] = Depends(require_roles("SUPER_ADMIN")),
) -> ResponseEnvelope[dict]:
    from modules.reviews.infrastructure.models.review_models import ReviewModel
    result = await db.execute(select(ReviewModel).where(ReviewModel.id == review_id))
    model = result.scalar_one_or_none()
    if model:
        model.is_flagged = False
        await db.commit()
    return ResponseEnvelope(data={"message": "Review approved successfully"})


@router.post("/{review_id}/reject", response_model=ResponseEnvelope[dict])
async def reject_review(
    review_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    _current_user: dict[str, Any] = Depends(require_roles("SUPER_ADMIN")),
) -> ResponseEnvelope[dict]:
    from modules.reviews.infrastructure.models.review_models import ReviewModel
    result = await db.execute(select(ReviewModel).where(ReviewModel.id == review_id))
    model = result.scalar_one_or_none()
    if model:
        await db.delete(model)
        await db.commit()
    return ResponseEnvelope(data={"message": "Review rejected successfully"})
