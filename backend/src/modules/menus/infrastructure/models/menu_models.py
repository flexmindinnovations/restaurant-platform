import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from shared.infrastructure.database import Base


class MenuModel(Base):
    __tablename__ = "menus"
    __table_args__ = {"schema": "menus"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    restaurant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)

    categories = relationship("CategoryModel", back_populates="menu", cascade="all, delete-orphan")
    items = relationship("MenuItemModel", back_populates="menu", cascade="all, delete-orphan")


class CategoryModel(Base):
    __tablename__ = "categories"
    __table_args__ = {"schema": "menus"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    menu_id = Column(
        UUID(as_uuid=True),
        ForeignKey("menus.menus.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    display_order = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)

    menu = relationship("MenuModel", back_populates="categories")


class MenuItemModel(Base):
    __tablename__ = "menu_items"
    __table_args__ = {"schema": "menus"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    menu_id = Column(
        UUID(as_uuid=True),
        ForeignKey("menus.menus.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category_id = Column(
        UUID(as_uuid=True),
        ForeignKey("menus.categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    restaurant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price_amount = Column(Numeric(precision=10, scale=2), nullable=False)
    price_currency = Column(String(3), default="USD", nullable=False)
    image_url = Column(String(500), nullable=True)
    display_order = Column(Integer, default=0, nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)
    dietary_labels = Column(JSONB, default=list, nullable=False)
    preparation_time_minutes = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)

    menu = relationship("MenuModel", back_populates="items")
    category = relationship("CategoryModel")
