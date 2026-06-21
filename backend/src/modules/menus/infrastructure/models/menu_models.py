import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.types import UserDefinedType

from shared.infrastructure.database import Base


class MenuModel(Base):
    __tablename__ = "menus"
    __table_args__ = (
        UniqueConstraint("restaurant_id", "name", name="uq_menus_restaurant_name"),
        {"schema": "menus"},
    )

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
    __table_args__ = (
        UniqueConstraint("menu_id", "name", name="uq_categories_menu_name"),
        {"schema": "menus"},
    )

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
    __table_args__ = (
        UniqueConstraint("menu_id", "category_id", "name", name="uq_menu_items_menu_category_name"),
        {"schema": "menus"},
    )

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
    price_currency = Column(String(3), default="INR", nullable=False)
    image_url = Column(String(500), nullable=True)
    display_order = Column(Integer, default=0, nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)
    dietary_labels = Column(JSONB, default=list, nullable=False)
    preparation_time_minutes = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)

    menu = relationship("MenuModel", back_populates="items")
    category = relationship("CategoryModel")
    modifier_groups = relationship("ModifierGroupModel", back_populates="menu_item", cascade="all, delete-orphan")
    embedding = relationship(
        "MenuItemEmbeddingModel", back_populates="menu_item", uselist=False, cascade="all, delete-orphan"
    )


class ModifierGroupModel(Base):
    __tablename__ = "modifier_groups"
    __table_args__ = {"schema": "menus"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    menu_item_id = Column(
        UUID(as_uuid=True),
        ForeignKey("menus.menu_items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    restaurant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    selection_type = Column(String(20), default="SINGLE", nullable=False)
    min_selections = Column(Integer, default=0, nullable=False)
    max_selections = Column(Integer, default=1, nullable=False)
    is_required = Column(Boolean, default=False, nullable=False)
    display_order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)

    menu_item = relationship("MenuItemModel", back_populates="modifier_groups")
    modifiers = relationship("ModifierModel", back_populates="modifier_group", cascade="all, delete-orphan")


class ModifierModel(Base):
    __tablename__ = "modifiers"
    __table_args__ = {"schema": "menus"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    modifier_group_id = Column(
        UUID(as_uuid=True),
        ForeignKey("menus.modifier_groups.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(255), nullable=False)
    price_adjustment_amount = Column(Numeric(precision=10, scale=2), default=0, nullable=False)
    price_adjustment_currency = Column(String(3), default="INR", nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)
    display_order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)

    modifier_group = relationship("ModifierGroupModel", back_populates="modifiers")


class Vector(UserDefinedType):
    def __init__(self, dim: int):
        self.dim = dim

    def get_col_spec(self, **_kw):
        return f"vector({self.dim})"


class MenuItemEmbeddingModel(Base):
    __tablename__ = "menu_item_embeddings"
    __table_args__ = {"schema": "menus"}

    menu_item_id = Column(
        UUID(as_uuid=True),
        ForeignKey("menus.menu_items.id", ondelete="CASCADE"),
        primary_key=True,
    )
    embedding = Column(Vector(768), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)

    menu_item = relationship("MenuItemModel", back_populates="embedding")
