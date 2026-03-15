import os
import json
from openai import OpenAI

# ── CLIENTS ────────────────────────────────────────────────────────────────────
# Primary: local Ollama on Computer 2 (free, LAN)
# Fallback: OpenAI (if Computer 2 is offline)

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://192.168.0.151:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

ollama_client = OpenAI(
    api_key="ollama",
    base_url=f"{OLLAMA_HOST}/v1"
)

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """You are Behique, an intelligent personal assistant for a creative, ADHD mind.

Your job is to classify every incoming thought, idea, or note into a structured format.

BROAD CATEGORIES (pick exactly one):
- CREATIVE: Any artistic or creative output — books, movies, scripts, songs, poems, artwork, games, stories, characters, worldbuilding
- BUSINESS: Entrepreneurial or financial thinking — startups, products, services, strategies, brands, investments, income streams
- KNOWLEDGE: Learning, research, insight, philosophy, frameworks, theories, reflections on how the world works
- PERSONAL: Self-development, goals, habits, health, wellness, relationships, emotional processing, memories, routines
- TECHNICAL: Apps, tools, systems, code, automations, inventions, product architecture

NICHES per category (pick the most specific):
CREATIVE → book, movie, script, song, poem, artwork, game, story, character, world, music, comedy, series
BUSINESS → startup, product, service, strategy, brand, investment, income, marketing, partnership, system
KNOWLEDGE → research, theory, insight, philosophy, framework, reflection, lesson, quote, concept
PERSONAL → goal, habit, health, wellness, relationship, memory, emotion, routine, mindset, affirmation
TECHNICAL → app, tool, automation, code, invention, architecture, integration, workflow

LIFE PILLAR (pick one or "general"):
- health: physical or mental wellbeing, energy, fitness, food, sleep, therapy, mindfulness
- wealth: money, income, business, investment, financial freedom
- relationships: family, friends, romance, community, connection, social
- general: doesn't clearly fit one pillar, or spans multiple

Respond ONLY with a valid JSON object in this exact format:
{
  "category": "CREATIVE",
  "niche": "book",
  "life_pillar": "wealth",
  "summary": "One sentence capturing the core idea",
  "tags": ["tag1", "tag2", "tag3"],
  "is_update_signal": false
}

is_update_signal: set to true if the message sounds like it's adding to, modifying, or following up on a previous idea
(e.g., "also", "and another thing", "update on", "I changed my mind", "adding to", "actually", "building on", "correction", "what if instead").
"""


def _classify_with_client(client: OpenAI, model: str, text: str) -> dict:
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text}
        ],
        temperature=0.2,
        response_format={"type": "json_object"}
    )

    result = response.choices[0].message.content
    classification = json.loads(result)

    required = ["category", "niche", "life_pillar", "summary", "tags", "is_update_signal"]
    for field in required:
        if field not in classification:
            raise ValueError(f"Missing field: {field}")

    return classification


def classify_input(text: str) -> dict:
    # Try Ollama first (free, local)
    try:
        return _classify_with_client(ollama_client, OLLAMA_MODEL, text)
    except Exception as ollama_err:
        pass

    # Fallback to OpenAI
    try:
        return _classify_with_client(openai_client, "gpt-4o-mini", text)
    except Exception:
        pass

    # Last resort safe fallback
    return {
        "category": "PERSONAL",
        "niche": "reflection",
        "life_pillar": "general",
        "summary": text[:100],
        "tags": ["uncategorized"],
        "is_update_signal": False
    }
