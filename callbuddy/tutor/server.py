#!/usr/bin/env python3
"""
Book-to-Agent RAG Tutor - FastAPI Server

Endpoints:
    POST /tutor/ask   - Query the tutor
    GET  /tutor/stats  - Ingestion statistics

Usage:
    pip install fastapi uvicorn
    python3 server.py
    # or: uvicorn server:app --host 0.0.0.0 --port 8096
"""

import json
from pathlib import Path

try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
except ImportError:
    print("FastAPI not installed. Run: pip install fastapi uvicorn")
    print("The query engine works without it: python3 query.py 'your question'")
    raise SystemExit(1)

from query import ask

BRAIN_DIR = Path(__file__).parent / "brain"
CHUNKS_FILE = BRAIN_DIR / "chunks.json"
INDEX_FILE = BRAIN_DIR / "index.json"

app = FastAPI(
    title="Book-to-Agent RAG Tutor",
    description="Turn ebooks and transcripts into interactive AI tutors",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    question: str
    top_k: int = 3


class AskResponse(BaseModel):
    answer: str
    sources: list[dict]
    ollama: bool


@app.post("/tutor/ask", response_model=AskResponse)
def tutor_ask(req: AskRequest):
    """Query the tutor with a question."""
    result = ask(req.question, req.top_k)
    return result


@app.get("/tutor/stats")
def tutor_stats():
    """Return ingestion statistics."""
    stats = {
        "files": 0,
        "chunks": 0,
        "index_terms": 0,
        "sources": [],
        "brain_exists": False,
    }

    if CHUNKS_FILE.exists():
        with open(CHUNKS_FILE, "r") as f:
            chunks = json.load(f)
        stats["chunks"] = len(chunks)
        sources = list(set(c["source"] for c in chunks))
        stats["files"] = len(sources)
        stats["sources"] = sources
        stats["brain_exists"] = True

    if INDEX_FILE.exists():
        with open(INDEX_FILE, "r") as f:
            index = json.load(f)
        stats["index_terms"] = len(index.get("inverted", {}))

    return stats


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8096)
