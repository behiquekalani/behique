"""
LLM-based listing content generator.
Takes product info + research data, outputs optimized listing content.

Supports Claude API (primary) and Ollama (free fallback).
"""

import json
import logging
import os

import requests

from core.types import ProductInput, ResearchResult, ListingContent

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert eBay listing copywriter. You write titles and descriptions that:
- Maximize search visibility (keyword-rich titles)
- Convert browsers to buyers (clear condition, value proposition)
- Follow eBay best practices (no keyword stuffing, accurate specifics)

Rules:
- Title: exactly 80 characters or less. Front-load the most important keywords.
- Description: clean HTML. Start with key features, then condition details, then shipping info.
- Item specifics: include Brand, Model, Color, Condition, and any category-relevant fields.
- Price: suggest based on the research data provided. Account for condition.
- Be honest about condition. Never misrepresent."""


def _build_user_prompt(product: ProductInput, research: ResearchResult) -> str:
    return f"""Create an eBay listing for this product:

Product: {product.name}
Condition: {product.condition}
Category: {research.category_name} (ID: {research.category_id})
{f'Notes: {product.notes}' if product.notes else ''}

Market Research:
- Average sold price: ${research.avg_sold_price:.2f}
- Median sold price: ${research.median_sold_price:.2f}
- Price range: ${research.min_sold_price:.2f} - ${research.max_sold_price:.2f}
- Average shipping cost: ${research.avg_shipping_cost:.2f}
{f'- Sell-through rate: {research.sell_through_rate:.1%}' if research.sell_through_rate else ''}

Top-selling titles for reference:
{chr(10).join(f'  - {t}' for t in research.sample_titles[:5])}

Common item specifics:
{json.dumps(research.common_specifics, indent=2)}

Respond in this exact JSON format:
{{
  "title": "string (max 80 chars)",
  "description": "string (HTML)",
  "item_specifics": {{"key": "value"}},
  "suggested_price": float,
  "suggested_condition": "string",
  "keywords": ["string"]
}}"""


class ContentGenerator:
    """
    Stage 2 adapter: generates listing content using an LLM.
    Tries Claude API first, falls back to Ollama if configured.
    """

    def __init__(self, provider: str = "claude", model: str = None):
        """
        provider: "claude" or "ollama"
        model: override model name (default: claude-haiku-4-5-20251001 / llama3.2)
        """
        self.provider = provider

        if provider == "claude":
            self.api_key = os.environ.get("ANTHROPIC_API_KEY")
            self.model = model or "claude-haiku-4-5-20251001"
            if not self.api_key:
                logger.warning("ANTHROPIC_API_KEY not set. Content generation will fail.")
        elif provider == "ollama":
            self.ollama_url = os.environ.get("OLLAMA_URL", "http://localhost:11434")
            self.model = model or "llama3.2"
        else:
            raise ValueError(f"Unknown provider: {provider}. Use 'claude' or 'ollama'.")

    def generate(self, product: ProductInput, research: ResearchResult) -> ListingContent:
        """Generate listing content from product + research data."""
        user_prompt = _build_user_prompt(product, research)

        if self.provider == "claude":
            raw = self._call_claude(user_prompt)
        else:
            raw = self._call_ollama(user_prompt)

        return self._parse_response(raw)

    def _call_claude(self, user_prompt: str) -> str:
        """Call Anthropic Messages API."""
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": self.model,
                "max_tokens": 1024,
                "system": SYSTEM_PROMPT,
                "messages": [{"role": "user", "content": user_prompt}],
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["content"][0]["text"]

    def _call_ollama(self, user_prompt: str) -> str:
        """Call local Ollama API."""
        resp = requests.post(
            f"{self.ollama_url}/api/generate",
            json={
                "model": self.model,
                "system": SYSTEM_PROMPT,
                "prompt": user_prompt,
                "stream": False,
            },
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()["response"]

    def _parse_response(self, raw: str) -> ListingContent:
        """Parse LLM JSON response into ListingContent."""
        # Strip markdown code fences if present
        text = raw.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1])

        data = json.loads(text)

        return ListingContent(
            title=data["title"][:80],
            description=data["description"],
            item_specifics=data.get("item_specifics", {}),
            suggested_price=float(data.get("suggested_price", 0)),
            suggested_condition=data.get("suggested_condition", "Used"),
            keywords=data.get("keywords", []),
        )
