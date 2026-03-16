---
name: idea-classifier
description: >
  Classifies incoming thoughts, ideas, and notes into Kalani's personal taxonomy:
  5 categories (CREATIVE, BUSINESS, KNOWLEDGE, PERSONAL, TECHNICAL) × specific niches
  × 4 life pillars (health, wealth, relationships, general). Trigger when a message
  looks like an idea dump, brain dump, voice memo transcript, or when the user sends
  a thought that needs to be captured and organized. Also trigger on "classify this",
  "save this idea", "capture this", or any unstructured thought that needs structure.
---

## What This Does

Takes any raw thought and returns a structured classification. This powers the idea
capture pipeline — every idea gets categorized so nothing gets lost in a flat list.

## Classification Schema

### Categories (pick exactly one)
- **CREATIVE**: Artistic or creative output — books, movies, scripts, songs, poems, artwork, games, stories, characters, worldbuilding
- **BUSINESS**: Entrepreneurial or financial — startups, products, services, strategies, brands, investments, income streams
- **KNOWLEDGE**: Learning and insight — research, theories, philosophy, frameworks, reflections
- **PERSONAL**: Self-development — goals, habits, health, wellness, relationships, emotional processing, routines
- **TECHNICAL**: Systems and tools — apps, automations, code, inventions, architecture, workflows

### Niches (pick the most specific)
```
CREATIVE  → book, movie, script, song, poem, artwork, game, story, character, world, music, comedy, series
BUSINESS  → startup, product, service, strategy, brand, investment, income, marketing, partnership, system
KNOWLEDGE → research, theory, insight, philosophy, framework, reflection, lesson, quote, concept
PERSONAL  → goal, habit, health, wellness, relationship, memory, emotion, routine, mindset, affirmation
TECHNICAL → app, tool, automation, code, invention, architecture, integration, workflow
```

### Life Pillars (pick one)
- **health**: physical or mental wellbeing, energy, fitness, food, sleep, therapy, mindfulness
- **wealth**: money, income, business, investment, financial freedom
- **relationships**: family, friends, romance, community, connection
- **general**: spans multiple or doesn't clearly fit one

### Update Signal
Set `is_update_signal: true` if the message sounds like it's adding to a previous idea:
"also", "and another thing", "update on", "I changed my mind", "actually", "building on", "correction", "what if instead"

## Output Format

Always return valid JSON:
```json
{
  "category": "BUSINESS",
  "niche": "product",
  "life_pillar": "wealth",
  "summary": "One sentence capturing the core idea",
  "tags": ["tag1", "tag2", "tag3"],
  "is_update_signal": false
}
```

## Routing

This classification should run on Ollama (llama3.2) when available — it's a simple
extraction task and doesn't need a frontier model. Fall back to GPT-4o-mini if Ollama
is unreachable.
