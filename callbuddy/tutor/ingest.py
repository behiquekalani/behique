#!/usr/bin/env python3
"""
Book-to-Agent RAG Tutor - Ingestion Pipeline

Scans a directory for .txt, .md, .pdf files, chunks them,
builds a TF-IDF inverted index. Pure Python, no external deps.

Usage:
    python3 ingest.py /path/to/transcripts/
"""

import json
import math
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

BRAIN_DIR = Path(__file__).parent / "brain"
CHUNKS_FILE = BRAIN_DIR / "chunks.json"
INDEX_FILE = BRAIN_DIR / "index.json"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf"}


def extract_text(filepath: Path) -> str:
    """Extract text from a file. PDF support is best-effort via basic parsing."""
    ext = filepath.suffix.lower()

    if ext in (".txt", ".md"):
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            return f.read()

    if ext == ".pdf":
        return _extract_pdf_text(filepath)

    return ""


def _extract_pdf_text(filepath: Path) -> str:
    """Extract text from PDF. Tries PyPDF2/pypdf if available, falls back to raw extraction."""
    # Try pypdf first
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(filepath))
        pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
        return "\n\n".join(pages)
    except ImportError:
        pass

    # Try PyPDF2
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(str(filepath))
        pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
        return "\n\n".join(pages)
    except ImportError:
        pass

    # Raw fallback - extract strings between stream markers
    try:
        with open(filepath, "rb") as f:
            data = f.read()
        text_parts = []
        # Find text between parentheses in PDF content streams
        for match in re.finditer(rb"\(([^)]+)\)", data):
            try:
                decoded = match.group(1).decode("utf-8", errors="ignore")
                if len(decoded) > 2 and any(c.isalpha() for c in decoded):
                    text_parts.append(decoded)
            except Exception:
                pass
        if text_parts:
            return " ".join(text_parts)
    except Exception:
        pass

    print(f"  WARNING: Could not extract text from PDF: {filepath.name}")
    print(f"           Install pypdf for better PDF support: pip install pypdf")
    return ""


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into chunks with overlap."""
    if not text.strip():
        return []

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunk = text[start:end]

        # Try to break at a sentence boundary
        if end < len(text):
            last_period = chunk.rfind(". ")
            last_newline = chunk.rfind("\n")
            break_at = max(last_period, last_newline)
            if break_at > size * 0.5:
                chunk = text[start:start + break_at + 1]
                end = start + break_at + 1

        chunks.append(chunk.strip())
        start = end - overlap

    return chunks


def tokenize(text: str) -> list[str]:
    """Simple tokenizer - lowercase, split on non-alphanumeric, filter short tokens."""
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    return [t for t in tokens if len(t) > 1]


def build_tfidf_index(chunks: list[dict]) -> dict:
    """Build an inverted index with TF-IDF weights."""
    # Document frequency: how many chunks contain each term
    df = defaultdict(int)
    # Term frequency per chunk
    tf_per_chunk = {}

    for chunk in chunks:
        chunk_id = chunk["id"]
        tokens = tokenize(chunk["text"])
        tf = defaultdict(int)
        for token in tokens:
            tf[token] += 1

        # Normalize TF
        max_tf = max(tf.values()) if tf else 1
        tf_per_chunk[chunk_id] = {t: count / max_tf for t, count in tf.items()}

        # Count DF
        for token in set(tokens):
            df[token] += 1

    n_docs = len(chunks)
    # IDF - use smoothed variant that works with small corpora
    idf = {}
    for term, freq in df.items():
        idf[term] = math.log((n_docs + 1) / (1 + freq)) + 1.0

    # Build inverted index: term -> [(chunk_id, tfidf_weight), ...]
    inverted = defaultdict(list)
    for chunk_id, tf in tf_per_chunk.items():
        for term, tf_val in tf.items():
            weight = tf_val * idf.get(term, 0)
            if weight > 0.001:
                inverted[term].append([chunk_id, round(weight, 4)])

    # Sort postings by weight descending
    for term in inverted:
        inverted[term].sort(key=lambda x: x[1], reverse=True)

    return {
        "inverted": dict(inverted),
        "idf": {k: round(v, 4) for k, v in idf.items()},
        "n_docs": n_docs,
    }


def scan_directory(directory: Path) -> list[Path]:
    """Find all supported files in directory recursively."""
    files = []
    for ext in SUPPORTED_EXTENSIONS:
        files.extend(directory.rglob(f"*{ext}"))
    return sorted(files)


def ingest(directory: str) -> dict:
    """Main ingestion pipeline."""
    source_dir = Path(directory).resolve()
    if not source_dir.is_dir():
        print(f"ERROR: {source_dir} is not a directory")
        sys.exit(1)

    BRAIN_DIR.mkdir(parents=True, exist_ok=True)

    files = scan_directory(source_dir)
    if not files:
        print(f"No supported files found in {source_dir}")
        print(f"Supported: {', '.join(SUPPORTED_EXTENSIONS)}")
        sys.exit(1)

    print(f"Found {len(files)} files in {source_dir}")

    all_chunks = []
    chunk_id = 0

    for filepath in files:
        print(f"  Processing: {filepath.name}")
        text = extract_text(filepath)
        if not text.strip():
            print(f"    Skipped (empty)")
            continue

        chunks = chunk_text(text)
        print(f"    {len(chunks)} chunks")

        for i, chunk_text_str in enumerate(chunks):
            all_chunks.append({
                "id": chunk_id,
                "text": chunk_text_str,
                "source": filepath.name,
                "source_path": str(filepath),
                "chunk_index": i,
                "total_chunks": len(chunks),
            })
            chunk_id += 1

    if not all_chunks:
        print("ERROR: No text extracted from any file")
        sys.exit(1)

    # Save chunks
    with open(CHUNKS_FILE, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)
    print(f"\nSaved {len(all_chunks)} chunks to {CHUNKS_FILE}")

    # Build and save index
    print("Building TF-IDF index...")
    index = build_tfidf_index(all_chunks)
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False)
    print(f"Saved index ({len(index['inverted'])} terms) to {INDEX_FILE}")

    stats = {
        "files": len(files),
        "chunks": len(all_chunks),
        "terms": len(index["inverted"]),
        "sources": list(set(c["source"] for c in all_chunks)),
    }
    print(f"\nDone. {stats['files']} files, {stats['chunks']} chunks, {stats['terms']} indexed terms.")
    return stats


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 ingest.py /path/to/transcripts/")
        sys.exit(1)

    ingest(sys.argv[1])
