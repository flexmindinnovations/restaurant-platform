import uuid

from sqlalchemy import Boolean, Column, DateTime, Double, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from shared.infrastructure.database import Base


class RestaurantModel(Base):
    __tablename__ = "restaurants"
    __table_args__ = {"schema": "restaurants"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    cuisine_types = Column(JSONB, default=list, nullable=False)
    address_street = Column(String(255), nullable=False)
    address_city = Column(String(100), nullable=False)
    address_state = Column(String(100), nullable=False)
    address_postal_code = Column(String(20), nullable=False)
    address_country = Column(String(100), nullable=False)
    address_latitude = Column(Double, nullable=True)
    address_longitude = Column(Double, nullable=True)
    phone = Column(String(50), nullable=False)
    email = Column(String(255), nullable=False)
    operating_hours = Column(JSONB, default=dict, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    rating_avg = Column(Numeric(precision=3, scale=2), default=0.00, nullable=False)
    total_reviews = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)
