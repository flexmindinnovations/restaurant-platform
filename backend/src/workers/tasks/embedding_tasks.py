import asyncio
import datetime
import pathlib

# Ensure the AI module can be loaded
import sys
import uuid

import structlog
from celery import shared_task
from sqlalchemy import select

from modules.menus.infrastructure.models.menu_models import MenuItemEmbeddingModel, MenuItemModel
from shared.infrastructure.database import get_session_factory

ai_path = str((pathlib.Path(__file__).parent / "../../../../ai/src").resolve())
if ai_path not in sys.path:
    sys.path.append(ai_path)

from embeddings.generator import MenuItemEmbeddingGenerator  # noqa: E402

logger = structlog.get_logger()


async def generate_menu_embeddings_async(menu_id: str) -> None:
    session_factory = get_session_factory()
    generator = MenuItemEmbeddingGenerator()
    menu_uuid = uuid.UUID(menu_id)

    async with session_factory() as session:
        stmt = select(MenuItemModel).where(MenuItemModel.menu_id == menu_uuid)
        result = await session.execute(stmt)
        items = result.scalars().all()

        if not items:
            logger.info("No menu items found for menu", menu_id=menu_id)
            return

        for item in items:
            try:
                embedding_vector = await generator.generate_for_item(
                    name=item.name, description=item.description, dietary_labels=item.dietary_labels
                )
            except Exception as e:
                logger.exception("Failed to generate embedding for menu item", item_id=item.id, error=str(e))
                continue

            try:
                emb_stmt = select(MenuItemEmbeddingModel).where(MenuItemEmbeddingModel.menu_item_id == item.id)
                emb_result = await session.execute(emb_stmt)
                existing_emb = emb_result.scalar_one_or_none()
            except Exception as e:
                logger.exception("Failed to query embedding for menu item", item_id=item.id, error=str(e))
                continue

            now = datetime.datetime.now(datetime.UTC)
            if existing_emb:
                existing_emb.embedding = embedding_vector
                existing_emb.updated_at = now
            else:
                new_emb = MenuItemEmbeddingModel(
                    menu_item_id=item.id, embedding=embedding_vector, created_at=now, updated_at=now
                )
                try:
                    session.add(new_emb)
                except Exception as e:
                    logger.exception("Failed to add embedding for menu item", item_id=item.id, error=str(e))

        await session.commit()
        logger.info("Successfully generated embeddings for menu", menu_id=menu_id)


@shared_task(name="workers.tasks.generate_menu_embeddings_task")
def generate_menu_embeddings_task(menu_id: str) -> None:
    asyncio.run(generate_menu_embeddings_async(menu_id))
