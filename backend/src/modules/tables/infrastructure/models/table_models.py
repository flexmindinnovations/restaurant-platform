import uuid

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, Text, Time, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from shared.infrastructure.database import Base


class SectionModel(Base):
    __tablename__ = "sections"
    __table_args__ = {"schema": "tables"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    restaurant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    display_order = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)

    tables = relationship("TableModel", back_populates="section", cascade="all, delete-orphan")


class TableModel(Base):
    __tablename__ = "tables"
    __table_args__ = (
        UniqueConstraint("restaurant_id", "number", name="uq_tables_restaurant_id_number"),
        {"schema": "tables"},
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    restaurant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    section_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tables.sections.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    number = Column(String(20), nullable=False)
    capacity_min = Column(Integer, default=1, nullable=False)
    capacity_max = Column(Integer, default=1, nullable=False)
    shape = Column(String(20), default="RECTANGULAR", nullable=False)
    position_x = Column(Integer, default=0, nullable=False)
    position_y = Column(Integer, default=0, nullable=False)
    status = Column(String(20), default="AVAILABLE", nullable=False)
    turn_time_minutes = Column(Integer, default=90, nullable=False)
    buffer_minutes = Column(Integer, default=15, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)

    section = relationship("SectionModel", back_populates="tables")
    reservations = relationship("ReservationModel", back_populates="table")


class ReservationModel(Base):
    __tablename__ = "reservations"
    __table_args__ = {"schema": "tables"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    restaurant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    table_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tables.tables.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    customer_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    customer_name = Column(String(255), nullable=False)
    customer_phone = Column(String(20), nullable=True)
    customer_email = Column(String(255), nullable=True)
    date = Column(Date, nullable=False, index=True)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    party_size = Column(Integer, nullable=False)
    status = Column(String(20), default="PENDING", nullable=False)
    special_requests = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)
    hold_until = Column(DateTime(timezone=True), nullable=True)
    seated_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    cancellation_reason = Column(Text, nullable=True)
    source = Column(String(20), default="PLATFORM", nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)

    table = relationship("TableModel", back_populates="reservations")


class WaitlistEntryModel(Base):
    __tablename__ = "waitlist_entries"
    __table_args__ = {"schema": "tables"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    restaurant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    customer_name = Column(String(255), nullable=False)
    customer_phone = Column(String(20), nullable=False)
    customer_id = Column(UUID(as_uuid=True), nullable=True)
    party_size = Column(Integer, nullable=False)
    estimated_wait_minutes = Column(Integer, default=0, nullable=False)
    queue_position = Column(Integer, default=0, nullable=False)
    status = Column(String(20), default="WAITING", nullable=False)
    preferred_section = Column(
        UUID(as_uuid=True),
        ForeignKey("tables.sections.id", ondelete="SET NULL"),
        nullable=True,
    )
    special_requests = Column(Text, nullable=True)
    notified_at = Column(DateTime(timezone=True), nullable=True)
    seated_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)
