#!/usr/bin/env python3
"""
Vault Context Engine — Graph-Aware Context Loading

Uses the vault knowledge graph + typed relationships to intelligently
select which vault files to load for any given topic or task.

Instead of dumb CWD→file mappings, this walks the graph:
  1. Resolve topic to a node (fuzzy match)
  2. Walk typed relationships (uses_tool, relates_to_project, etc.)
  3. BFS expand to depth 2 for wiki-linked neighbors
  4. Score each candidate by relevance (type weight × distance)
  5. Return top-N file paths, ordered by relevance

Usage as library:
    from vault_context_engine import VaultContextEngine
    engine = VaultContextEngine()
    files = engine.context_for("eBay")          # → relevant vault files
    files = engine.context_for("pricing")        # → fuzzy match → pricing-related
    files = engine.context_for_prompt("help me list a product on eBay")

Usage as CLI:
    python3 vault_context_engine.py "eBay"
    python3 vault_context_engine.py "pricing" --top 10
    python3 vault_context_engine.py --prompt "help me debug the bridge connection"
    python3 vault_context_engine.py --cwd tools/ebay-listing-assistant
"""

import os
import re
import sys
import json
import time
import hashlib
import argparse
from collections import defaultdict
from pathlib import Path

# Add tools/ to path so we can import graph_query
TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)

from graph_query import VaultGraph

BEHIQUE = os.path.expanduser("~/behique")
CEIBA = os.path.join(BEHIQUE, "Ceiba")

# Node type relevance weights (higher = more likely to be useful context)
TYPE_WEIGHTS = {
    "project": 1.0,
    "tool": 0.9,
    "system": 0.9,
    "design": 0.8,
    "decision": 0.8,
    "pattern": 0.7,
    "knowledge": 0.6,
    "goal": 0.6,
    "check-in": 0.3,
    "session": 0.2,
    "identity": 0.5,
    "note": 0.4,
    "unknown": 0.3,
}

# Typed relationship relevance multipliers
# If a node is connected via a typed relationship, it gets a relevance boost
REL_WEIGHTS = {
    "uses_tool": 0.95,
    "uses_system": 0.90,
    "relates_to_project": 0.85,
    "follows_pattern": 0.70,
    "implements_decision": 0.80,
    "logged_in_session": 0.30,
}

# Keywords that map to known topics (for prompt parsing)
TOPIC_KEYWORDS = {
    "ebay": ["eBay-Listing-Assistant", "pricing", "shipping", "listing"],
    "listing": ["eBay-Listing-Assistant"],
    "shopify": ["Shopify-Store"],
    "behiquebot": ["BehiqueBot"],
    "bot": ["BehiqueBot"],
    "telegram": ["BehiqueBot", "Telegram-Scraper-SaaS"],
    "bridge": ["SYS_Bridge", "architecture-spine"],
    "cobo": ["SYS_Bridge", "architecture-spine"],
    "scraper": ["Google-Trends-Scraper", "Telegram-Scraper-SaaS"],
    "trends": ["Google-Trends-Scraper"],
    "n8n": ["n8n-Agency"],
    "automation": ["n8n-Agency"],
    "vault": ["SYS_Vault_Graph", "VAULT_INDEX"],
    "graph": ["SYS_Vault_Graph", "vault_grapher"],
    "memory": ["ceiba-memory-protocol-cmp", "SYS_AI_Cluster"],
    "cmp": ["ceiba-memory-protocol-cmp"],
    "kernel": ["agent-kernel-architecture", "SYS_AI_Cluster"],
    "cluster": ["SYS_AI_Cluster", "architecture-spine"],
    "grpc": ["ceiba-cobo-grpc-prototype", "ceiba-cobo-communication-protocol-ccp"],
    "pricing": ["eBay-Listing-Assistant"],
    "shipping": ["eBay-Listing-Assistant"],
    "dashboard": ["SYS_Vault_Graph"],
    "quest": ["MISSIONS"],
    "revenue": ["eBay-Listing-Assistant", "Shopify-Store"],
    "ebook": ["AI-Ebook"],
    "video": ["AI-Ebook"],  # same creative content track
}


class VaultContextEngine:
    """Graph-aware context loader for the vault."""

    # In-memory cache: hash → (timestamp, results)
    _cache = {}
    _CACHE_TTL = 300  # 5 minutes

    def __init__(self, graph_path=None):
        self.graph = VaultGraph(graph_path) if graph_path else VaultGraph()

    def _cache_key(self, *args) -> str:
        """Create a stable cache key from arguments."""
        raw = json.dumps(args, sort_keys=True, default=str)
        return hashlib.md5(raw.encode()).hexdigest()

    def _get_cached(self, key: str):
        """Return cached result if fresh, else None."""
        if key in self._cache:
            ts, results = self._cache[key]
            if time.time() - ts < self._CACHE_TTL:
                return results
            del self._cache[key]
        return None

    def _set_cached(self, key: str, results):
        """Store results in cache. Evict oldest if cache > 50 entries."""
        if len(self._cache) > 50:
            oldest_key = min(self._cache, key=lambda k: self._cache[k][0])
            del self._cache[oldest_key]
        self._cache[key] = (time.time(), results)

    def context_for(self, topic: str, top_n: int = 7, include_content: bool = False) -> list:
        """
        Get the most relevant vault files for a topic.

        Returns list of dicts:
          [{"node": name, "path": abs_path, "score": float, "type": str, "via": str}, ...]
        """
        # Check cache first (skip if content requested — always fresh)
        if not include_content:
            cache_key = self._cache_key("context_for", topic, top_n)
            cached = self._get_cached(cache_key)
            if cached is not None:
                return cached

        candidates = {}  # node_name → {score, via}

        # 1. Direct node resolution
        resolved = self.graph._resolve_name(topic)
        if resolved:
            self._add_candidate(candidates, resolved, 1.0, "direct_match")

        # 2. Search for fuzzy matches
        search_hits = self.graph.search(topic)
        for i, hit in enumerate(search_hits[:5]):
            # Decay score for lower-ranked search results
            base_score = 0.9 - (i * 0.1)
            self._add_candidate(candidates, hit, base_score, "search")

        # 3. Check keyword map
        topic_lower = topic.lower()
        for keyword, node_names in TOPIC_KEYWORDS.items():
            if keyword in topic_lower:
                for node_name in node_names:
                    resolved_kw = self.graph._resolve_name(node_name)
                    if resolved_kw:
                        self._add_candidate(candidates, resolved_kw, 0.85, f"keyword:{keyword}")

        # 4. Walk typed relationships from all candidates (copy to avoid mutation during iteration)
        seed_nodes = list(candidates.keys())
        for node in seed_nodes:
            # Forward relationships: this node uses_tool X, relates_to_project Y, etc.
            rels = self.graph.relationships(node)
            for rel_type, targets in rels.items():
                rel_weight = REL_WEIGHTS.get(rel_type, 0.5)
                for target in targets:
                    parent_score = candidates[node]["score"]
                    child_score = parent_score * rel_weight
                    self._add_candidate(candidates, target, child_score, f"rel:{rel_type}")

            # Reverse relationships: what uses this node?
            rev_rels = self.graph.reverse_relationships(node)
            for rel_type, sources in rev_rels.items():
                rel_weight = REL_WEIGHTS.get(rel_type, 0.5) * 0.8  # Slightly less relevant
                for source in sources:
                    parent_score = candidates[node]["score"]
                    child_score = parent_score * rel_weight
                    self._add_candidate(candidates, source, child_score, f"rev_rel:{rel_type}")

        # 5. BFS expand 1 hop from top candidates for wiki-link neighbors
        top_seeds = sorted(candidates.keys(), key=lambda n: -candidates[n]["score"])[:3]
        for node in top_seeds:
            neighbors = self.graph.neighbors(node)
            for neighbor in neighbors:
                if neighbor not in candidates:
                    parent_score = candidates[node]["score"]
                    self._add_candidate(candidates, neighbor, parent_score * 0.4, "wiki_neighbor")

        # 6. Apply type weights
        scored = []
        for node_name, info in candidates.items():
            node_data = self.graph.nodes.get(node_name, {})
            node_type = node_data.get("type", "unknown")
            type_weight = TYPE_WEIGHTS.get(node_type, 0.3)
            final_score = info["score"] * type_weight

            # Resolve to absolute file path
            rel_path = node_data.get("path", "")
            if rel_path:
                abs_path = os.path.join(BEHIQUE, rel_path)
            else:
                abs_path = ""

            scored.append({
                "node": node_name,
                "path": abs_path,
                "score": round(final_score, 3),
                "type": node_type,
                "via": info["via"],
            })

        # Sort by score, filter to files that exist
        scored.sort(key=lambda x: -x["score"])
        result = [s for s in scored if s["path"] and os.path.exists(s["path"])][:top_n]

        # 7. Optionally load file content (first N lines)
        if include_content:
            for entry in result:
                try:
                    lines = Path(entry["path"]).read_text(encoding="utf-8").splitlines()[:40]
                    entry["content"] = "\n".join(lines)
                except Exception:
                    entry["content"] = ""

        # Cache result (only if no content — content makes it too large)
        if not include_content:
            cache_key = self._cache_key("context_for", topic, top_n)
            self._set_cached(cache_key, result)

        return result

    def context_for_prompt(self, prompt: str, top_n: int = 7) -> list:
        """
        Extract topics from a natural language prompt and find relevant context.
        Combines results from all detected topics with fusion scoring.
        """
        # Cache check
        cache_key = self._cache_key("context_for_prompt", prompt, top_n)
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        topics = self._extract_topics(prompt)
        if not topics:
            # Fallback: use the whole prompt as a search query
            return self.context_for(prompt, top_n=top_n)

        # Fusion scoring: nodes that appear in multiple topic queries get boosted
        node_hits = defaultdict(list)  # node → list of (result, topic)
        for topic in topics:
            results = self.context_for(topic, top_n=top_n * 2)
            for r in results:
                node_hits[r["node"]].append((r, topic))

        # Merge with fusion boost: +15% per additional topic match
        all_results = {}
        for node, hits in node_hits.items():
            best = max(hits, key=lambda h: h[0]["score"])
            result = best[0].copy()
            fusion_boost = 1.0 + 0.15 * (len(hits) - 1)
            result["score"] = round(result["score"] * fusion_boost, 3)
            if len(hits) > 1:
                result["via"] += f" +fusion({len(hits)} topics)"
            all_results[node] = result

        merged = sorted(all_results.values(), key=lambda x: -x["score"])
        result = merged[:top_n]

        self._set_cached(cache_key, result)
        return result

    def context_summary(self, topic: str, top_n: int = 5) -> str:
        """
        One-liner context summary for a topic — useful for quick lookups.
        Returns formatted string: "topic → node1 (type), node2 (type), ..."
        """
        results = self.context_for(topic, top_n=top_n)
        if not results:
            return f"{topic} → (no matches)"
        items = [f"{r['node']} ({r['type']}, {r['score']})" for r in results]
        return f"{topic} → {', '.join(items)}"

    def context_for_cwd(self, cwd: str, top_n: int = 7) -> list:
        """
        Get context based on current working directory.
        Extracts project/tool names from the path.
        """
        # Normalize path
        cwd_lower = cwd.lower().replace("\\", "/")

        topics = []

        # Extract folder names that might be project/tool names
        parts = cwd_lower.split("/")
        for part in parts:
            # Skip common non-informative parts
            if part in ("", "users", "kalani", "behique", "tools", "ceiba",
                       "src", "lib", "core", "providers", "ai", "media", "storage"):
                continue
            # Clean up and add as topic
            clean = part.replace("-", " ").replace("_", " ")
            topics.append(clean)

        # Also check keyword map against full path
        for keyword in TOPIC_KEYWORDS:
            if keyword in cwd_lower:
                topics.append(keyword)

        if not topics:
            topics = ["vault"]  # Default: load vault overview

        # Merge results from all path-derived topics
        all_results = {}
        for topic in topics:
            results = self.context_for(topic, top_n=top_n * 2)
            for r in results:
                node = r["node"]
                if node not in all_results or r["score"] > all_results[node]["score"]:
                    all_results[node] = r

        merged = sorted(all_results.values(), key=lambda x: -x["score"])
        return merged[:top_n]

    def format_context(self, results: list, max_lines: int = 30) -> str:
        """Format context results as a readable string for injection."""
        if not results:
            return ""

        parts = []
        for r in results:
            try:
                lines = Path(r["path"]).read_text(encoding="utf-8").splitlines()[:max_lines]
                content = "\n".join(lines)
                parts.append(f"[{r['node']}] (type:{r['type']}, relevance:{r['score']})\n{content}")
            except Exception:
                continue

        return "\n---\n".join(parts)

    def _add_candidate(self, candidates: dict, node: str, score: float, via: str):
        """Add or update a candidate, keeping the highest score."""
        if node in candidates:
            if score > candidates[node]["score"]:
                candidates[node] = {"score": score, "via": via}
        else:
            candidates[node] = {"score": score, "via": via}

    def _extract_topics(self, prompt: str) -> list:
        """Extract likely topic names from a prompt using multi-strategy NLP."""
        topics = []
        prompt_lower = prompt.lower()

        # 1. Check keyword map (highest priority)
        for keyword in TOPIC_KEYWORDS:
            if keyword in prompt_lower:
                topics.append(keyword)

        # 2. Extract quoted strings
        quoted = re.findall(r'"([^"]+)"', prompt)
        topics.extend(quoted)

        # 3. Extract CamelCase words (project names like BehiqueBot, OpenClaw)
        caps = re.findall(r'\b[A-Z][a-zA-Z]+(?:[A-Z][a-zA-Z]+)+\b', prompt)
        topics.extend(caps)

        # 4. Extract hyphenated compound terms (ebay-listing, vault-graph)
        hyphenated = re.findall(r'\b[a-zA-Z]+-[a-zA-Z]+(?:-[a-zA-Z]+)*\b', prompt)
        topics.extend(hyphenated)

        # 5. Extract file/tool references (.py files, path fragments)
        files = re.findall(r'\b[\w_]+\.(?:py|sh|js|html|json|md)\b', prompt)
        for f in files:
            # Strip extension and use as topic
            name = f.rsplit('.', 1)[0]
            topics.append(name)

        # 6. Extract action→domain patterns ("list on ebay" → ebay, "fix the bridge" → bridge)
        action_patterns = [
            r'(?:list|sell|post|publish)\s+(?:on\s+)?(\w+)',
            r'(?:fix|debug|update|upgrade|build|deploy)\s+(?:the\s+)?(\w+)',
            r'(?:check|scan|query|search)\s+(?:the\s+)?(\w+)',
        ]
        for pattern in action_patterns:
            matches = re.findall(pattern, prompt_lower)
            for m in matches:
                if m not in ('the', 'a', 'an', 'it', 'this', 'that', 'my', 'our'):
                    topics.append(m)

        # 7. Deduplicate while preserving order
        seen = set()
        unique = []
        for t in topics:
            t_lower = t.lower()
            if t_lower not in seen:
                seen.add(t_lower)
                unique.append(t)

        return unique


# ============ CLI ============
def main():
    parser = argparse.ArgumentParser(description="Vault Context Engine — Graph-aware context loading")
    parser.add_argument("topic", nargs="?", help="Topic to find context for")
    parser.add_argument("--prompt", help="Natural language prompt to extract topics from")
    parser.add_argument("--cwd", help="Working directory to derive context from")
    parser.add_argument("--top", type=int, default=7, help="Number of results (default: 7)")
    parser.add_argument("--content", action="store_true", help="Include file content in output")
    parser.add_argument("--json", action="store_true", dest="as_json", help="Output as JSON")
    parser.add_argument("--format", action="store_true", help="Output formatted context block")

    args = parser.parse_args()

    if not args.topic and not args.prompt and not args.cwd:
        parser.print_help()
        return

    engine = VaultContextEngine()

    if args.prompt:
        results = engine.context_for_prompt(args.prompt, top_n=args.top)
    elif args.cwd:
        results = engine.context_for_cwd(args.cwd, top_n=args.top)
    else:
        results = engine.context_for(args.topic, top_n=args.top, include_content=args.content)

    if args.as_json:
        print(json.dumps(results, indent=2))
    elif args.format:
        print(engine.format_context(results))
    else:
        print(f"Context for: {args.topic or args.prompt or args.cwd}")
        print(f"Found {len(results)} relevant nodes:\n")
        for r in results:
            via = r['via']
            print(f"  {r['score']:.3f}  {r['node']:<35} ({r['type']:<10})  via {via}")
            if r.get("content"):
                preview = r["content"][:120].replace("\n", " ")
                print(f"         {preview}...")
        print()


if __name__ == "__main__":
    main()
