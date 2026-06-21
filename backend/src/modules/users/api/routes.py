import uuid
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db_session
from modules.users.api.dependencies import (
    get_create_profile_handler,
    get_profile_query_handler,
    get_update_profile_handler,
)
from modules.users.api.schemas import UpdateProfileRequest, UserProfileResponse
from modules.users.application.commands.create_profile import (
    CreateProfileCommand,
    CreateProfileHandler,
    parse_names_from_email,
)
from modules.users.application.commands.update_profile import UpdateProfileCommand, UpdateProfileHandler
from modules.users.application.queries.get_profile import GetProfileHandler, GetProfileQuery
from shared.api.response import ResponseEnvelope
from shared.api.security import get_current_user, require_roles
from shared.domain.exceptions import NotFoundException

router = APIRouter()


@router.get("", response_model=ResponseEnvelope[UserProfileResponse])
async def get_profile(
    current_user: dict[str, Any] = Depends(get_current_user),
    query_handler: GetProfileHandler = Depends(get_profile_query_handler),
    create_handler: CreateProfileHandler = Depends(get_create_profile_handler),
) -> ResponseEnvelope[UserProfileResponse]:
    account_id = uuid.UUID(current_user["sub"])
    query = GetProfileQuery(account_id=account_id)
    try:
        profile_dto = await query_handler.handle(query)
    except NotFoundException:
        email = current_user.get("email") or "admin@quickbite.com"
        first_name, last_name = parse_names_from_email(email)
        create_cmd = CreateProfileCommand(
            account_id=account_id,
            first_name=first_name,
            last_name=last_name,
        )
        await create_handler.handle(create_cmd)
        profile_dto = await query_handler.handle(query)

    return ResponseEnvelope(
        data=UserProfileResponse(
            id=profile_dto.id,
            account_id=profile_dto.account_id,
            first_name=profile_dto.first_name,
            last_name=profile_dto.last_name,
            display_name=profile_dto.display_name,
            avatar_url=profile_dto.avatar_url,
            preferred_language=profile_dto.preferred_language,
            created_at=profile_dto.created_at,
            updated_at=profile_dto.updated_at,
        )
    )


@router.patch("", response_model=ResponseEnvelope[dict])
async def update_profile(
    request: UpdateProfileRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    command_handler: UpdateProfileHandler = Depends(get_update_profile_handler),
) -> ResponseEnvelope[dict]:
    account_id = uuid.UUID(current_user["sub"])
    command = UpdateProfileCommand(
        account_id=account_id,
        first_name=request.first_name,
        last_name=request.last_name,
        display_name=request.display_name,
        avatar_url=request.avatar_url,
        preferred_language=request.preferred_language,
    )
    await command_handler.handle(command)
    return ResponseEnvelope(data={"message": "Profile updated successfully"})


admin_router = APIRouter()


@admin_router.get("", response_model=ResponseEnvelope[dict])
async def admin_list_users(
    skip: int = 0,
    limit: int = 10,
    search: str | None = None,
    role: str | None = None,
    db: AsyncSession = Depends(get_db_session),
    _current_user: dict[str, Any] = Depends(require_roles("SUPER_ADMIN")),
) -> ResponseEnvelope[dict]:
    from sqlalchemy import select

    from modules.identity.infrastructure.models.account_model import AccountModel
    from modules.users.infrastructure.models.profile_model import ProfileModel

    query = select(AccountModel, ProfileModel).join(ProfileModel, AccountModel.id == ProfileModel.account_id)
    if search:
        search_term = f"%{search}%"
        query = query.where(
            AccountModel.email.ilike(search_term)
            | ProfileModel.first_name.ilike(search_term)
            | ProfileModel.last_name.ilike(search_term)
            | ProfileModel.display_name.ilike(search_term)
        )

    result = await db.execute(query)
    rows = result.all()

    users_list = []
    for acc, prof in rows:
        acc_roles = acc.roles if isinstance(acc.roles, list) else []
        if role and role != "ALL" and role not in acc_roles:
            continue
        users_list.append({
            "id": str(acc.id),
            "email": acc.email,
            "phone_number": acc.phone_number or "",
            "first_name": prof.first_name,
            "last_name": prof.last_name,
            "display_name": prof.display_name or "",
            "roles": acc_roles,
            "is_active": acc.is_active,
            "avatar_url": prof.avatar_url or "",
            "created_at": acc.created_at.isoformat() if acc.created_at else "",
        })

    total = len(users_list)
    paginated = users_list[skip : skip + limit]
    return ResponseEnvelope(data={"items": paginated, "total": total})


@admin_router.patch("/{user_id}/role", response_model=ResponseEnvelope[dict])
async def admin_update_user_role(
    user_id: uuid.UUID,
    request: dict,
    db: AsyncSession = Depends(get_db_session),
    _current_user: dict[str, Any] = Depends(require_roles("SUPER_ADMIN")),
) -> ResponseEnvelope[dict]:
    from sqlalchemy import update

    from modules.identity.infrastructure.models.account_model import AccountModel

    roles = request.get("roles", [])
    await db.execute(update(AccountModel).where(AccountModel.id == user_id).values(roles=roles))
    await db.commit()
    return ResponseEnvelope(data={"message": "User roles updated successfully"})


@admin_router.post("/{user_id}/toggle-status", response_model=ResponseEnvelope[dict])
async def admin_toggle_user_status(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    _current_user: dict[str, Any] = Depends(require_roles("SUPER_ADMIN")),
) -> ResponseEnvelope[dict]:
    from sqlalchemy import select

    from modules.identity.infrastructure.models.account_model import AccountModel

    result = await db.execute(select(AccountModel).where(AccountModel.id == user_id))
    acc = result.scalar_one_or_none()
    if acc:
        acc.is_active = not acc.is_active
        await db.commit()
    return ResponseEnvelope(data={"message": "User status toggled successfully"})
