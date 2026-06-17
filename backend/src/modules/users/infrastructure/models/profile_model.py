import uuid

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID

from shared.infrastructure.database import Base


class ProfileModel(Base):
    __tablename__ = "profiles"
    __table_args__ = {"schema": "users"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), nullable=False, unique=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    display_name = Column(String(200), nullable=True)
    avatar_url = Column(String(255), nullable=True)
    preferred_language = Column(String(10), default="en", nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)
