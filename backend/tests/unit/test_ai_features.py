import pathlib
import sys

import pytest

# Ensure AI module is in import path
ai_path = str((pathlib.Path(__file__).parent / "../../src/../../ai/src").resolve())
if ai_path not in sys.path:
    sys.path.append(ai_path)

from embeddings.generator import MenuItemEmbeddingGenerator  # noqa: E402
from gateway.client import GeminiClient  # noqa: E402
from models.sentiment_classifier import SentimentClassifier  # noqa: E402


@pytest.mark.asyncio
async def test_gemini_client_mock_embedding():
    client = GeminiClient(api_key=None)
    embedding = await client.embed_content("Pizza")
    assert len(embedding) == 768
    embedding2 = await client.embed_content("Pizza")
    assert embedding == embedding2


@pytest.mark.asyncio
async def test_gemini_client_mock_generate():
    client = GeminiClient(api_key=None)
    response = await client.generate_content("What is on the menu?")
    assert "menu" in response.lower() or "recommend" in response.lower()


@pytest.mark.asyncio
async def test_menu_item_embedding_generator():
    generator = MenuItemEmbeddingGenerator()
    embedding = await generator.generate_for_item("Burger", "Tasty beef burger", ["Gluten-free"])
    assert len(embedding) == 768


@pytest.mark.asyncio
async def test_sentiment_classifier():
    classifier = SentimentClassifier()
    res = await classifier.classify("The food was delicious and amazing!")
    assert res == "POSITIVE"

    res2 = await classifier.classify("Horrible service and terrible cold pizza.")
    assert res2 == "NEGATIVE"

    res3 = await classifier.classify("")
    assert res3 == "NEUTRAL"
