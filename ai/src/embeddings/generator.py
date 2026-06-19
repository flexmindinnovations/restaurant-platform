import os
import sys

# Ensure that the gateway package is discoverable if ai/src is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gateway.client import GeminiClient

class MenuItemEmbeddingGenerator:
    def __init__(self, client: GeminiClient | None = None):
        self.client = client or GeminiClient()

    async def generate_for_item(
        self,
        name: str,
        description: str | None,
        dietary_labels: list[str] | None = None
    ) -> list[float]:
        labels = dietary_labels or []
        label_str = f" Dietary labels: {', '.join(labels)}." if labels else ""
        desc = description or ""
        text = f"Menu Item: {name}. Description: {desc}.{label_str}"
        return await self.client.embed_content(text)
