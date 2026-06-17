import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UpdateProfileRequest(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    display_name: str | None = None
    avatar_url: str | None = None
    preferred_language: str | None = None


class UserProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    account_id: uuid.UUID
    first_name: str
    last_name: str
    display_name: str | None
    avatar_url: str | None
    preferred_language: str
    created_at: datetime
    updated_at: datetime
