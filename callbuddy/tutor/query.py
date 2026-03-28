#!/usr/bin/env python3
"""
Book-to-Agent RAG Tutor - Query Engine

Searches ingested chunks using TF-IDF similarity.
Optionally sends to Ollama for synthesized answers.

Usage:
    python3 query.py "explain the concept in chapter 4"
    python3 query.py "what is the main argument" --top_k 5
"""

import json
import math
import re
import sys
import urllib.request
import urllib.error
from collections import defaultdict
from pathlib import Path

BRAIN_DIR = Path(__file__).parent / "brain"
CHUNKS_FILE = BRAIN_DIR / "chunks.json"
INDEX_FILE = BRAIN_DIR / "index.json"

OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3"


def tokenize(text: str) -> list[str]:
    """Same tokenizer as ingest - must match."""
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    return [t for t in tokens if len(t) > 1]


def load_brain() -> tuple[list[dict], dict]:
    """Load chunks and index from disk."""
    if not CHUNKS_FILE.exists() or not INDEX_FILE.exists():
        print("ERROR: No brain data found. Run ingest.py first.")
        print(f"  Expected: {CHUNKS_FILE}")
        print(f"  Expected: {INDEX_FILE}")
        sys.exit(1)

    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        index = json.load(f)

    return chunks, index


def search(question: str, chunks: list[dict], index: dict, top_k: int = 3) -> list[dict]:
    """Search chunks using TF-IDF cosine similarity."""
    query_tokens = tokenize(question)
    if not query_tokens:
        return []

    inverted = index["inverted"]
    idf = index["idf"]

    # Score each chunk
    scores = defaultdict(float)
    for token in query_tokens:
        if token not in inverted:
            continue
        query_weight = idf.get(token, 0)
        for chunk_id, doc_weight in inverted[token]:
            scores[chunk_id] += query_weight * doc_weight

    if not scores:
        return []

    # Normalize and sort
    max_score = max(scores.values())
    results = []
    for chunk_id, score in sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]:
        chunk = chunks[chunk_id]
        results.append({
            "id": chunk_id,
            "text": chunk["text"],
            "source": chunk["source"],
            "chunk_index": chunk["chunk_index"],
            "total_chunks": chunk["total_chunks"],
            "score": round(score / max_score, 4) if max_score > 0 else 0,
        })

    return results


def check_ollama() -> bool:
    """Check if Ollama is running."""
    try:
        req = urllib.request.Request(OLLAMA_URL, method="GET")
        resp = urllib.request.urlopen(req, timeout=2)
        return resp.status == 200
    except Exception:
        return False


def query_ollama(question: str, context_chunks: list[dict]) -> str:
    """Send question + context to Ollama for synthesis."""
    context = "\n\n---\n\n".join(
        f"[Source: {c['source']}, chunk {c['chunk_index']+1}/{c['total_chunks']}]\n{c['text']}"
        for c in context_chunks
    )

    prompt = f"""You are a knowledgeable tutor. Answer the question using ONLY the provided context.
If the context doesn't contain enough information, say so honestly.
Cite your sources by mentioning the source file name.

CONTEXT:
{context}

QUESTION: {question}

ANSWER:"""

    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.3,
            "num_predict": 512,
        }
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        resp = urllib.request.urlopen(req, timeout=60)
        data = json.loads(resp.read().decode("utf-8"))
        return data.get("response", "No response from model.")
    except Exception as e:
        return f"Ollama error: {e}"


def ask(question: str, top_k: int = 3) -> dict:
    """Main query function. Returns answer + sources."""
    chunks, index = load_brain()
    results = search(question, chunks, index, top_k)

    if not results:
        return {
            "answer": "No relevant chunks found for your question. Try different keywords.",
            "sources": [],
            "ollama": False,
        }

    has_ollama = check_ollama()

    if has_ollama:
        answer = query_ollama(question, results)
    else:
        # Format raw chunks as the answer
        parts = []
        for r in results:
            parts.append(
                f"Based on [{r['source']}], chunk {r['chunk_index']+1}/{r['total_chunks']} "
                f"(relevance: {r['score']:.0%}):\n{r['text']}"
            )
        answer = "\n\n---\n\n".join(parts)

    return {
        "answer": answer,
        "sources": [
            {
                "file": r["source"],
                "chunk": r["chunk_index"],
                "total": r["total_chunks"],
                "score": r["score"],
            }
            for r in results
        ],
        "ollama": has_ollama,
    }


def format_output(result: dict) -> str:
    """Format result for CLI display."""
    lines = []

    if result["ollama"]:
        lines.append("[Ollama synthesized answer]\n")
    else:
        lines.append("[Raw chunk retrieval - Ollama not available]\n")

    lines.append(result["answer"])
    lines.append("\n\n--- Sources ---")
    for s in result["sources"]:
        lines.append(f"  {s['file']} (chunk {s['chunk']+1}/{s['total']}, score: {s['score']:.0%})")

    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: python3 query.py "your question here" [--top_k N]')
        sys.exit(1)

    question = sys.argv[1]
    top_k = 3

    if "--top_k" in sys.argv:
        idx = sys.argv.index("--top_k")
        if idx + 1 < len(sys.argv):
            top_k = int(sys.argv[idx + 1])

    result = ask(question, top_k)
    print(format_output(result))
