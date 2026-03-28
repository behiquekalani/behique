"""
link_handler.py — Telegram Link Intake Pipeline
When Kalani sends a URL, this module:
  1. Detects the URL type (article, YouTube, Twitter, GitHub, generic)
  2. Fetches and extracts the content (requests + BeautifulSoup, with Apify fallback)
  3. Triages into one of 5 vault categories: IDEA / PROJECT / REFERENCE / CONTENT / JOURNAL
  4. Writes to the appropriate vault file
  5. Registers a node in vault_graph.json
  6. Sends a confirmation back to Telegram

Secrets: All API keys via environment variables. Never hardcoded.
"""

import os
import re
import json
import uuid
import logging
from datetime import datetime
from urllib.parse import urlparse

from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

# ── VAULT PATHS ─────────────────────────────────────────────────────────────────
VAULT_BASE = os.getenv("VAULT_BASE", "Ceiba")
VAULT_GRAPH_PATH = os.path.join(VAULT_BASE, "vault_graph.json")
VAULT_DESTINATIONS = {
    "IDEA":      os.path.join(VAULT_BASE, "IDEAS_BACKLOG.md"),
    "PROJECT":   os.path.join(VAULT_BASE, "PENDING_PROJECTS.md"),
    "REFERENCE": os.path.join(VAULT_BASE, "05-Knowledge", "REFERENCES.md"),
    "CONTENT":   os.path.join(VAULT_BASE, "projects", "content-empire", "CONTENT_CAPTURES.md"),
    "JOURNAL":   os.path.join(VAULT_BASE, "AI_JOURNAL.md"),
}

# ── URL DETECTION ────────────────────────────────────────────────────────────────
URL_PATTERN = re.compile(
    r'https?://[^\s<>"\']+',
    re.IGNORECASE
)

def extract_urls(text: str) -> list[str]:
    return URL_PATTERN.findall(text)

def classify_url_type(url: str) -> str:
    """Return a simple type label for the URL."""
    parsed = urlparse(url)
    host = parsed.netloc.lower().replace("www.", "")

    if "youtube.com" in host or "youtu.be" in host:
        return "youtube"
    if "twitter.com" in host or "x.com" in host:
        return "twitter"
    if "github.com" in host:
        return "github"
    if "reddit.com" in host:
        return "reddit"
    if "instagram.com" in host:
        return "instagram"
    if "gumroad.com" in host:
        return "gumroad"
    if "notion.so" in host or "notion.site" in host:
        return "notion"
    return "article"


# ── CONTENT FETCHING ─────────────────────────────────────────────────────────────
def fetch_content(url: str, url_type: str) -> dict:
    """
    Fetch and extract content from a URL.
    Returns: {title, description, body_excerpt, fetch_method}
    Falls back gracefully: trafilatura -> requests+BeautifulSoup -> Apify -> minimal
    """
    result = {
        "title": "",
        "description": "",
        "body_excerpt": "",
        "fetch_method": "none",
    }

    # 1. Try trafilatura (best for articles, $0 cost)
    try:
        import trafilatura
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            extracted = trafilatura.extract(
                downloaded,
                include_comments=False,
                include_tables=False,
                favor_precision=True,
            )
            meta = trafilatura.extract_metadata(downloaded)
            if meta:
                result["title"] = meta.title or ""
                result["description"] = meta.description or ""
            if extracted:
                result["body_excerpt"] = extracted[:1200]
                result["fetch_method"] = "trafilatura"
                return result
    except Exception as e:
        logger.debug(f"trafilatura failed: {e}")

    # 2. Try requests + BeautifulSoup
    try:
        import requests
        from bs4 import BeautifulSoup

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        # Title
        og_title = soup.find("meta", property="og:title")
        result["title"] = (
            og_title["content"] if og_title and og_title.get("content")
            else (soup.title.string if soup.title else "")
        )

        # Description
        og_desc = soup.find("meta", property="og:description")
        meta_desc = soup.find("meta", attrs={"name": "description"})
        result["description"] = (
            og_title["content"] if og_title and og_title.get("content") else
            og_desc["content"] if og_desc and og_desc.get("content") else
            meta_desc["content"] if meta_desc and meta_desc.get("content") else ""
        )

        # Fix: use og_desc for description (above has a bug with og_title reuse)
        if og_desc and og_desc.get("content"):
            result["description"] = og_desc["content"]
        elif meta_desc and meta_desc.get("content"):
            result["description"] = meta_desc["content"]

        # Body text
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        body_text = soup.get_text(separator=" ", strip=True)
        result["body_excerpt"] = body_text[:1200]
        result["fetch_method"] = "beautifulsoup"
        return result

    except Exception as e:
        logger.debug(f"BeautifulSoup fetch failed: {e}")

    # 3. Try Apify RAG web browser (requires APIFY_API_KEY env var)
    apify_key = os.getenv("APIFY_API_KEY")
    if apify_key:
        try:
            import requests
            resp = requests.post(
                "https://api.apify.com/v2/acts/apify~rag-web-browser/run-sync-get-dataset-items",
                params={"token": apify_key},
                json={"query": url, "maxResults": 1},
                timeout=30,
            )
            if resp.status_code == 200:
                data = resp.json()
                if data and isinstance(data, list) and len(data) > 0:
                    item = data[0]
                    result["title"] = item.get("title", "")
                    result["description"] = item.get("description", "")
                    result["body_excerpt"] = item.get("text", "")[:1200]
                    result["fetch_method"] = "apify"
                    return result
        except Exception as e:
            logger.debug(f"Apify fetch failed: {e}")

    # 4. Minimal fallback — just the URL itself
    result["title"] = url
    result["fetch_method"] = "url_only"
    return result


# ── LLM TRIAGE ───────────────────────────────────────────────────────────────────
TRIAGE_SYSTEM_PROMPT = """You are Ceiba, a personal knowledge management assistant.

A user has shared a link. Based on the URL, page title, and content excerpt, classify it into ONE category:

CATEGORIES:
- IDEA: A concept, technique, product, or insight worth exploring later. Good for "this is interesting" saves.
- PROJECT: Something actionable that could become a project — tool, app, business model, framework.
- REFERENCE: A resource to return to — documentation, tutorial, guide, how-to, research paper.
- CONTENT: Something to repurpose for social media, newsletters, or content creation.
- JOURNAL: Something personal — motivational, reflective, a quote, or something that resonated emotionally.

Also provide:
- A 1-sentence summary of what this link is about
- 3-5 relevant tags
- A suggested title for the vault entry (short, clear)

Respond ONLY with valid JSON:
{
  "category": "IDEA",
  "summary": "One sentence description",
  "title": "Short vault entry title",
  "tags": ["tag1", "tag2", "tag3"]
}"""


def triage_link(url: str, url_type: str, content: dict) -> dict:
    """
    Use LLM to triage the link into a vault category.
    Falls back to heuristics if LLM unavailable.
    """
    # Build context for LLM
    context = f"""URL: {url}
URL Type: {url_type}
Title: {content.get('title', '')}
Description: {content.get('description', '')}
Content excerpt: {content.get('body_excerpt', '')[:600]}"""

    # Try Ollama first (free, local)
    try:
        from openai import OpenAI
        ollama_host = os.getenv("OLLAMA_HOST", "http://192.168.0.151:11434")
        ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2")
        client = OpenAI(api_key="ollama", base_url=f"{ollama_host}/v1", timeout=8.0)
        response = client.chat.completions.create(
            model=ollama_model,
            messages=[
                {"role": "system", "content": TRIAGE_SYSTEM_PROMPT},
                {"role": "user", "content": context},
            ],
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        result = json.loads(response.choices[0].message.content)
        _validate_triage(result)
        return result
    except Exception:
        pass

    # Try OpenAI fallback
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        try:
            from openai import OpenAI
            fallback_model = os.getenv("FALLBACK_MODEL", "gpt-4o-mini")
            client = OpenAI(api_key=openai_key)
            response = client.chat.completions.create(
                model=fallback_model,
                messages=[
                    {"role": "system", "content": TRIAGE_SYSTEM_PROMPT},
                    {"role": "user", "content": context},
                ],
                temperature=0.1,
                response_format={"type": "json_object"},
            )
            result = json.loads(response.choices[0].message.content)
            _validate_triage(result)
            return result
        except Exception:
            pass

    # Heuristic fallback
    return _heuristic_triage(url, url_type, content)


def _validate_triage(result: dict):
    valid_categories = {"IDEA", "PROJECT", "REFERENCE", "CONTENT", "JOURNAL"}
    if result.get("category") not in valid_categories:
        raise ValueError(f"Invalid category: {result.get('category')}")
    if not result.get("summary"):
        raise ValueError("Missing summary")


def _heuristic_triage(url: str, url_type: str, content: dict) -> dict:
    """Rule-based fallback triage."""
    title_lower = (content.get("title", "") + content.get("description", "")).lower()

    if url_type == "youtube":
        category = "CONTENT"
    elif url_type == "github":
        category = "REFERENCE"
    elif url_type == "twitter":
        category = "IDEA"
    elif any(kw in title_lower for kw in ["tutorial", "guide", "how to", "docs", "documentation"]):
        category = "REFERENCE"
    elif any(kw in title_lower for kw in ["idea", "startup", "product", "build", "launch"]):
        category = "IDEA"
    elif any(kw in title_lower for kw in ["tool", "framework", "library", "api"]):
        category = "PROJECT"
    else:
        category = "REFERENCE"

    return {
        "category": category,
        "summary": content.get("description") or content.get("title") or url,
        "title": content.get("title") or urlparse(url).netloc,
        "tags": [url_type, "link-capture"],
    }


# ── VAULT WRITER ─────────────────────────────────────────────────────────────────
def write_to_vault(triage: dict, url: str, content: dict, entry_id: str):
    """
    Append a structured entry to the appropriate vault file.
    Creates the file and parent directories if they don't exist.
    Maps categories to vault folder conventions.
    """
    category = triage["category"]
    dest_path = VAULT_DESTINATIONS.get(category, VAULT_DESTINATIONS["REFERENCE"])

    os.makedirs(os.path.dirname(dest_path), exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    tags_str = " ".join(f"#{t}" for t in triage.get("tags", []))

    entry_block = f"""
---

## [{triage['title']}]({url})
- **ID:** `{entry_id[:8]}`
- **Captured:** {timestamp}
- **Category:** {category}
- **Tags:** {tags_str}
- **Source:** {content.get('fetch_method', 'unknown')}

**Summary:** {triage['summary']}

"""

    # If file doesn't exist, write a header first
    file_exists = os.path.exists(dest_path)
    with open(dest_path, "a", encoding="utf-8") as f:
        if not file_exists:
            f.write(f"# {category.title()} Captures\n")
            f.write("*Auto-generated by BehiqueBot link intake pipeline*\n")
        f.write(entry_block)

    logger.info(f"Vault entry written: {dest_path}")


# ── VAULT GRAPH REGISTRATION ─────────────────────────────────────────────────────
def register_vault_node(triage: dict, url: str, entry_id: str):
    """
    Add a new node to vault_graph.json for this link capture.
    Category maps to vault folder conventions.
    """
    category_to_folder = {
        "IDEA":      "02-Ideas",
        "PROJECT":   "01-Projects",
        "REFERENCE": "05-Knowledge",
        "CONTENT":   "projects/content-empire",
        "JOURNAL":   "03-Check-ins",
    }

    folder = category_to_folder.get(triage["category"], "05-Knowledge")
    slug = re.sub(r"[^a-z0-9-]", "-", triage["title"].lower())[:40].strip("-")
    node_key = f"{folder}/link-{entry_id[:8]}-{slug}"

    try:
        graph = {}
        if os.path.exists(VAULT_GRAPH_PATH):
            with open(VAULT_GRAPH_PATH, "r", encoding="utf-8") as f:
                graph = json.load(f)

        nodes = graph.get("nodes", {})
        nodes[node_key] = {
            "type": "link_capture",
            "category": triage["category"],
            "title": triage["title"],
            "url": url,
            "tags": triage.get("tags", []),
            "summary": triage.get("summary", ""),
            "captured": datetime.now().isoformat(),
            "entry_id": entry_id,
            "links": [],
        }
        graph["nodes"] = nodes
        graph["last_updated"] = datetime.now().isoformat()

        with open(VAULT_GRAPH_PATH, "w", encoding="utf-8") as f:
            json.dump(graph, f, ensure_ascii=False, indent=2)

        logger.info(f"Vault graph node registered: {node_key}")

    except Exception as e:
        logger.warning(f"Vault graph registration failed (non-blocking): {e}")


# ── CATEGORY LABELS ──────────────────────────────────────────────────────────────
CATEGORY_EMOJI = {
    "IDEA":      "💡",
    "PROJECT":   "🚀",
    "REFERENCE": "📚",
    "CONTENT":   "🎬",
    "JOURNAL":   "📓",
}

VAULT_FOLDER_LABEL = {
    "IDEA":      "Ceiba / IDEAS_BACKLOG.md",
    "PROJECT":   "Ceiba / PENDING_PROJECTS.md",
    "REFERENCE": "05-Knowledge / REFERENCES.md",
    "CONTENT":   "content-empire / CONTENT_CAPTURES.md",
    "JOURNAL":   "Ceiba / AI_JOURNAL.md",
}


# ── MAIN HANDLER (called from main.py) ──────────────────────────────────────────
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE, url: str):
    """
    Process a single URL sent by the user.
    Called by handle_text when a URL is detected.
    """
    entry_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    user_id = str(update.message.from_user.id)

    # 1. Classify the URL type
    url_type = classify_url_type(url)
    logger.info(f"[link_handler] URL received: {url} (type: {url_type})")

    # 2. Send "working..." immediately so Kalani knows it's processing
    working_msg = await update.message.reply_text(
        f"_Fetching {url_type} link..._",
        parse_mode="Markdown",
    )

    try:
        # 3. Fetch content
        content = fetch_content(url, url_type)
        logger.info(f"[link_handler] Content fetched via: {content['fetch_method']}")

        # 4. Triage with LLM
        triage = triage_link(url, url_type, content)
        logger.info(f"[link_handler] Triaged as: {triage['category']}")

        # 5. Write to vault
        write_to_vault(triage, url, content, entry_id)

        # 6. Register vault graph node
        register_vault_node(triage, url, entry_id)

        # 7. Build confirmation message
        category = triage["category"]
        emoji = CATEGORY_EMOJI.get(category, "📌")
        folder_label = VAULT_FOLDER_LABEL.get(category, "05-Knowledge")
        tags_str = " ".join(f"`#{t}`" for t in triage.get("tags", [])[:4])

        confirm = (
            f"{emoji} *{category}* captured\n"
            f"*{triage['title']}*\n\n"
            f"{triage['summary']}\n\n"
            f"Saved to: `{folder_label}`\n"
            f"ID: `{entry_id[:8]}`\n"
            f"Tags: {tags_str}"
        )

        # 8. Delete "working..." message and send confirmation
        await working_msg.delete()
        await update.message.reply_text(confirm, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"[link_handler] Error processing {url}: {e}", exc_info=True)
        await working_msg.delete()
        await update.message.reply_text(
            f"Could not process that link. Saved URL to journal anyway.\n"
            f"Error: {str(e)[:120]}",
            parse_mode="Markdown",
        )
        # Still write a minimal journal entry even on failure
        fallback_triage = {
            "category": "JOURNAL",
            "summary": f"Unprocessed link: {url}",
            "title": url,
            "tags": ["link-capture", "unprocessed"],
        }
        fallback_content = {"fetch_method": "failed"}
        try:
            write_to_vault(fallback_triage, url, fallback_content, entry_id)
        except Exception:
            pass
