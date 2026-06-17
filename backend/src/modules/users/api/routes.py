import uuid
from typing import Any

from fastapi import APIRouter, Depends

from modules.users.api.dependencies import get_profile_query_handler, get_update_profile_handler
from modules.users.api.schemas import UpdateProfileRequest, UserProfileResponse
from modules.users.application.commands.update_profile import UpdateProfileCommand, UpdateProfileHandler
from modules.users.application.queries.get_profile import GetProfileHandler, GetProfileQuery
from shared.api.response import ResponseEnvelope
from shared.api.security import get_current_user

router = APIRouter()


@router.get("", response_model=ResponseEnvelope[UserProfileResponse])
async def get_profile(
    current_user: dict[str, Any] = Depends(get_current_user),
    query_handler: GetProfileHandler = Depends(get_profile_query_handler),
) -> ResponseEnvelope[UserProfileResponse]:
    account_id = uuid.UUID(current_user["sub"])
    query = GetProfileQuery(account_id=account_id)
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
