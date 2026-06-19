import os
import random
import httpx
import structlog

logger = structlog.get_logger()

class GeminiClient:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"

    async def embed_content(self, text: str) -> list[float]:
        if not self.api_key:
            logger.warning("GEMINI_API_KEY is missing, returning mock embedding")
            return self._mock_embedding(text)

        url = f"{self.base_url}/text-embedding-004:embedContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "model": "models/text-embedding-004",
            "content": {
                "parts": [{"text": text}]
            }
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, headers=headers, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                return data["embedding"]["values"]
            except Exception as e:
                logger.error("Failed to generate embedding from Gemini API, falling back to mock", error=str(e))
                return self._mock_embedding(text)

    async def generate_content(
        self,
        contents: list[dict] | str,
        system_instruction: str | None = None
    ) -> str:
        if not self.api_key:
            logger.warning("GEMINI_API_KEY is missing, returning mock response")
            return self._mock_generate_content(contents)

        url = f"{self.base_url}/gemini-1.5-flash:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}

        # Format input content correctly
        if isinstance(contents, str):
            formatted_contents = [{"role": "user", "parts": [{"text": contents}]}]
        else:
            formatted_contents = []
            for item in contents:
                role = item.get("role", "user")
                # Handle possible different structures for input message parts
                text_content = ""
                if "text" in item:
                    text_content = item["text"]
                elif "parts" in item:
                    parts = item["parts"]
                    if isinstance(parts, list) and len(parts) > 0:
                        if isinstance(parts[0], dict):
                            text_content = parts[0].get("text", "")
                        else:
                            text_content = str(parts[0])
                    else:
                        text_content = str(parts)
                formatted_contents.append({
                    "role": role,
                    "parts": [{"text": text_content}]
                })

        payload = {"contents": formatted_contents}
        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, headers=headers, timeout=30.0)
                response.raise_for_status()
                data = response.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return parts[0].get("text", "")
                raise ValueError("Empty or invalid response structure from Gemini API")
            except Exception as e:
                logger.error("Failed to generate content from Gemini API, falling back to mock", error=str(e))
                return self._mock_generate_content(contents)

    def _mock_embedding(self, text: str) -> list[float]:
        # Generate a deterministic mock vector of 768 dimensions
        rng = random.Random(text)
        vector = [rng.uniform(-1.0, 1.0) for _ in range(768)]
        # Normalize
        norm = sum(x * x for x in vector) ** 0.5
        if norm > 0:
            vector = [x / norm for x in vector]
        return vector

    def _mock_generate_content(self, contents: list[dict] | str) -> str:
        prompt = ""
        if isinstance(contents, str):
            prompt = contents
        elif isinstance(contents, list) and contents:
            last_item = contents[-1]
            if "text" in last_item:
                prompt = last_item["text"]
            elif "parts" in last_item:
                parts = last_item["parts"]
                if isinstance(parts, list) and len(parts) > 0 and isinstance(parts[0], dict):
                    prompt = parts[0].get("text", "")
                else:
                    prompt = str(parts)

        prompt_lower = prompt.lower()
        if "menu" in prompt_lower:
            return "Sure! I can recommend some menu items. We have delicious pizzas, fresh salads, and exquisite desserts."
        elif "order" in prompt_lower:
            return "I'd be happy to help you check the status of your order. Could you please provide your order ID?"
        elif "refund" in prompt_lower:
            return "For refunds, please contact our customer support line or submit a request directly through the app."
        else:
            return f"Thank you for reaching out to customer support. This is a mock assistant. You said: '{prompt}'"
