import os
import sys

# Ensure gateway package is discoverable
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gateway.client import GeminiClient

class SentimentClassifier:
    def __init__(self, client: GeminiClient | None = None):
        self.client = client or GeminiClient()

    async def classify(self, text: str) -> str:
        if not text or not text.strip():
            return "NEUTRAL"

        prompt = (
            "Analyze the sentiment of the following restaurant review. "
            "Respond with exactly one word: POSITIVE, NEGATIVE, or NEUTRAL.\n\n"
            f"Review: \"{text}\""
        )

        try:
            response = await self.client.generate_content(
                contents=prompt,
                system_instruction="You are a sentiment analysis engine. You output only POSITIVE, NEGATIVE, or NEUTRAL."
            )
            sentiment = response.strip().upper()
            # Clean up the output in case there's punctuation
            sentiment = "".join(c for c in sentiment if c.isalnum())
            if sentiment in ["POSITIVE", "NEGATIVE", "NEUTRAL"]:
                return sentiment
        except Exception:
            pass

        # Rule-based fallback
        lower_text = text.lower()
        positive_words = ["good", "great", "delicious", "amazing", "love", "excellent", "best", "perfect", "friendly", "fresh", "tasty"]
        negative_words = ["bad", "worst", "terrible", "horrible", "cold", "late", "slow", "disappointed", "rude", "poor", "wrong"]

        pos_count = sum(1 for word in positive_words if word in lower_text)
        neg_count = sum(1 for word in negative_words if word in lower_text)

        if pos_count > neg_count:
            return "POSITIVE"
        elif neg_count > pos_count:
            return "NEGATIVE"
        return "NEUTRAL"
