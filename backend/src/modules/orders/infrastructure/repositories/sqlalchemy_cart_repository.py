import contextlib
import uuid
from datetime import datetime
from decimal import Decimal

import orjson
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.orders.application.ports.cart_repository import CartRepository
from modules.orders.domain.entities.cart import Cart, CartItem
from modules.orders.infrastructure.models.cart_models import CartItemModel, CartModel
from shared.domain.value_objects import Money


class SqlAlchemyCartRepository(CartRepository):
    def __init__(self, session: AsyncSession, redis: Redis) -> None:
        self._session = session
        self._redis = redis

    def _cache_key(self, customer_id: uuid.UUID) -> str:
        return f"cart:{customer_id}"

    def _serialize(self, cart: Cart) -> bytes:
        data = {
            "id": str(cart.id),
            "restaurant_id": str(cart.restaurant_id) if cart.restaurant_id else None,
            "created_at": cart.created_at.isoformat(),
            "updated_at": cart.updated_at.isoformat(),
            "items": [
                {
                    "id": str(item.id),
                    "menu_item_id": str(item.menu_item_id),
                    "name": item.name,
                    "unit_price_amount": str(item.unit_price.amount),
                    "unit_price_currency": item.unit_price.currency,
                    "quantity": item.quantity,
                    "special_instructions": item.special_instructions,
                }
                for item in cart.items
            ],
        }
        return orjson.dumps(data)

    def _deserialize(self, data_bytes: bytes) -> Cart:
        data = orjson.loads(data_bytes)
        items = [CartItem(
                    id=uuid.UUID(item_data["id"]),
                    menu_item_id=uuid.UUID(item_data["menu_item_id"]),
                    name=item_data["name"],
                    unit_price=Money(
                        amount=Decimal(item_data["unit_price_amount"]),
                        currency=item_data["unit_price_currency"],
                    ),
                    quantity=item_data["quantity"],
                    special_instructions=item_data["special_instructions"],
                ) for item_data in data["items"]]
        restaurant_id = uuid.UUID(data["restaurant_id"]) if data["restaurant_id"] else None
        return Cart(
            id=uuid.UUID(data["id"]),
            restaurant_id=restaurant_id,
            items=items,
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )

    async def get_by_customer_id(self, customer_id: uuid.UUID) -> Cart | None:
        # 1. Try fetching from Valkey Cache
        with contextlib.suppress(Exception):
            cached_data = await self._redis.get(self._cache_key(customer_id))
            if cached_data:
                return self._deserialize(cached_data)

        # 2. Fetch from Database
        result = await self._session.execute(select(CartModel).where(CartModel.id == customer_id))
        model = result.scalar_one_or_none()
        if not model:
            return None

        # Map to domain
        items = [
            CartItem(
                id=item.id,
                menu_item_id=item.menu_item_id,
                name=item.name,
                unit_price=Money(
                    amount=Decimal(str(item.price_amount)),
                    currency=item.price_currency,
                ),
                quantity=item.quantity,
                special_instructions=item.special_instructions,
            )
            for item in model.items
        ]
        cart = Cart(
            id=model.id,
            restaurant_id=model.restaurant_id,
            items=items,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

        # Cache back to Valkey
        with contextlib.suppress(Exception):
            await self._redis.setex(self._cache_key(customer_id), 86400, self._serialize(cart))

        return cart

    async def save(self, cart: Cart) -> None:
        # 1. Save to Valkey Cache (with 24h TTL)
        with contextlib.suppress(Exception):
            await self._redis.setex(self._cache_key(cart.id), 86400, self._serialize(cart))

        # 2. Save to Database (PostgreSQL)
        result = await self._session.execute(select(CartModel).where(CartModel.id == cart.id))
        model = result.scalar_one_or_none()

        if not model:
            model = CartModel(
                id=cart.id,
                restaurant_id=cart.restaurant_id,
                created_at=cart.created_at,
                updated_at=cart.updated_at,
            )
            self._session.add(model)
        else:
            model.restaurant_id = cart.restaurant_id
            model.updated_at = cart.updated_at

        # Synchronize items list (delete-orphan takes care of removed items)
        existing_items_map = {item.id: item for item in model.items}

        new_items_list = []
        for item in cart.items:
            existing = existing_items_map.get(item.id)
            if existing:
                existing.quantity = item.quantity
                existing.special_instructions = item.special_instructions
                new_items_list.append(existing)
            else:
                new_item_model = CartItemModel(
                    id=item.id,
                    cart_id=cart.id,
                    menu_item_id=item.menu_item_id,
                    name=item.name,
                    price_amount=item.unit_price.amount,
                    price_currency=item.unit_price.currency,
                    quantity=item.quantity,
                    special_instructions=item.special_instructions,
                )
                new_items_list.append(new_item_model)

        model.items = new_items_list

    async def delete(self, customer_id: uuid.UUID) -> None:
        # 1. Delete from Valkey Cache
        with contextlib.suppress(Exception):
            await self._redis.delete(self._cache_key(customer_id))

        # 2. Delete from Database
        result = await self._session.execute(select(CartModel).where(CartModel.id == customer_id))
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)
