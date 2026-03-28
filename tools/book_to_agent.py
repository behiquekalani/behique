#!/usr/bin/env python3
"""
Book-to-Agent: Turn any book/PDF into an interactive AI tutor.

Usage:
    python3 book_to_agent.py book.pdf              # Load book and start chatting
    python3 book_to_agent.py book.pdf --index-only  # Just build the index
    python3 book_to_agent.py --list                 # Show indexed books

Dependencies: requests, PyPDF2
    pip install requests PyPDF2
"""

import argparse
import hashlib
import json
import math
import os
import re
import sys
import textwrap
from collections import Counter
from datetime import datetime
from pathlib import Path

try:
    import requests
except ImportError:
    print("Missing dependency: requests")
    print("Run: pip install requests")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

DATA_DIR = Path.home() / ".book_agent"
INDEX_DIR = DATA_DIR / "indexes"
HISTORY_DIR = DATA_DIR / "history"
OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "qwen2.5:7b"
CHUNK_TARGET_WORDS = 500
TOP_K = 3

for d in [DATA_DIR, INDEX_DIR, HISTORY_DIR]:
    d.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Text extraction
# ---------------------------------------------------------------------------

def extract_text_from_pdf(filepath: str) -> str:
    """Extract text from a PDF file using PyPDF2."""
    try:
        from PyPDF2 import PdfReader
    except ImportError:
        print("Missing dependency: PyPDF2")
        print("Run: pip install PyPDF2")
        sys.exit(1)

    reader = PdfReader(filepath)
    pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            pages.append(text)
    return "\n\n".join(pages)


def extract_text_from_file(filepath: str) -> str:
    """Extract text from PDF, markdown, or plain text files."""
    ext = Path(filepath).suffix.lower()
    if ext == ".pdf":
        return extract_text_from_pdf(filepath)
    elif ext in (".txt", ".md", ".markdown", ".rst", ".text"):
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    else:
        # Try reading as plain text
        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                return f.read()
        except Exception:
            print(f"Cannot read file: {filepath}")
            sys.exit(1)


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------

def detect_chapters(text: str) -> list[str]:
    """Try to split text by chapter/heading markers. Returns sections."""
    # Common chapter patterns
    patterns = [
        r'\n(?=Chapter\s+\d)',
        r'\n(?=CHAPTER\s+\d)',
        r'\n(?=Part\s+[IVXLC]+)',
        r'\n(?=PART\s+[IVXLC]+)',
        r'\n(?=#{1,3}\s)',  # Markdown headings
    ]

    for pattern in patterns:
        sections = re.split(pattern, text)
        if len(sections) > 2:
            return [s.strip() for s in sections if s.strip()]

    return []


def chunk_text(text: str, target_words: int = CHUNK_TARGET_WORDS) -> list[dict]:
    """
    Split text into chunks. Tries chapter-based splitting first,
    then falls back to word-count based splitting with paragraph boundaries.
    """
    chunks = []

    # Try chapter-based splitting
    chapters = detect_chapters(text)

    if chapters:
        for i, chapter in enumerate(chapters):
            # If a chapter is too long, sub-chunk it
            words = chapter.split()
            if len(words) > target_words * 2:
                sub_chunks = _chunk_by_words(chapter, target_words)
                for j, sc in enumerate(sub_chunks):
                    # Extract a heading from first line if possible
                    first_line = sc.split("\n")[0][:80]
                    chunks.append({
                        "id": f"ch{i+1}_part{j+1}",
                        "heading": first_line,
                        "text": sc,
                        "word_count": len(sc.split()),
                    })
            else:
                first_line = chapter.split("\n")[0][:80]
                chunks.append({
                    "id": f"ch{i+1}",
                    "heading": first_line,
                    "text": chapter,
                    "word_count": len(words),
                })
    else:
        # Fall back to paragraph-aware word chunking
        sub_chunks = _chunk_by_words(text, target_words)
        for i, sc in enumerate(sub_chunks):
            first_line = sc.split("\n")[0][:80]
            chunks.append({
                "id": f"chunk_{i+1}",
                "heading": first_line,
                "text": sc,
                "word_count": len(sc.split()),
            })

    return chunks


def _chunk_by_words(text: str, target_words: int) -> list[str]:
    """Split text into chunks of roughly target_words, breaking at paragraphs."""
    paragraphs = re.split(r'\n\s*\n', text)
    chunks = []
    current = []
    current_count = 0

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        words = len(para.split())

        if current_count + words > target_words and current:
            chunks.append("\n\n".join(current))
            current = [para]
            current_count = words
        else:
            current.append(para)
            current_count += words

    if current:
        chunks.append("\n\n".join(current))

    return chunks


# ---------------------------------------------------------------------------
# TF-IDF search index (no heavy deps)
# ---------------------------------------------------------------------------

class SearchIndex:
    """Simple TF-IDF search index using only stdlib."""

    def __init__(self, chunks: list[dict]):
        self.chunks = chunks
        self.vocab: dict[str, int] = {}
        self.idf: dict[str, float] = {}
        self.tf_vectors: list[dict[str, float]] = []
        self._build()

    def _tokenize(self, text: str) -> list[str]:
        """Lowercase, strip punctuation, split into tokens."""
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        tokens = text.split()
        # Remove very short tokens and common stopwords
        stopwords = {
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'could', 'should', 'may', 'might', 'can', 'shall',
            'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from',
            'as', 'into', 'through', 'during', 'before', 'after', 'above',
            'below', 'between', 'and', 'but', 'or', 'nor', 'not', 'so',
            'yet', 'both', 'either', 'neither', 'each', 'every', 'all',
            'any', 'few', 'more', 'most', 'other', 'some', 'such', 'no',
            'only', 'own', 'same', 'than', 'too', 'very', 'just', 'if',
            'then', 'it', 'its', 'this', 'that', 'these', 'those', 'he',
            'she', 'they', 'we', 'you', 'i', 'me', 'him', 'her', 'us',
            'them', 'my', 'your', 'his', 'our', 'their', 'what', 'which',
            'who', 'whom', 'where', 'when', 'why', 'how', 'about',
        }
        return [t for t in tokens if len(t) > 1 and t not in stopwords]

    def _build(self):
        """Build TF-IDF vectors for all chunks."""
        n = len(self.chunks)
        doc_freq: Counter = Counter()
        tf_raw: list[Counter] = []

        for chunk in self.chunks:
            tokens = self._tokenize(chunk["text"])
            tf = Counter(tokens)
            tf_raw.append(tf)
            for token in set(tokens):
                doc_freq[token] += 1

        # Compute IDF
        for term, df in doc_freq.items():
            self.idf[term] = math.log((n + 1) / (df + 1)) + 1

        # Compute TF-IDF vectors (normalized)
        for tf in tf_raw:
            vec = {}
            total = sum(tf.values()) or 1
            for term, count in tf.items():
                tf_val = count / total
                vec[term] = tf_val * self.idf.get(term, 1.0)
            # Normalize
            norm = math.sqrt(sum(v * v for v in vec.values())) or 1
            vec = {k: v / norm for k, v in vec.items()}
            self.tf_vectors.append(vec)

    def search(self, query: str, top_k: int = TOP_K) -> list[dict]:
        """Search for the most relevant chunks given a query string."""
        tokens = self._tokenize(query)
        if not tokens:
            return self.chunks[:top_k]

        # Build query vector
        q_tf = Counter(tokens)
        total = sum(q_tf.values()) or 1
        q_vec = {}
        for term, count in q_tf.items():
            tf_val = count / total
            q_vec[term] = tf_val * self.idf.get(term, 1.0)
        norm = math.sqrt(sum(v * v for v in q_vec.values())) or 1
        q_vec = {k: v / norm for k, v in q_vec.items()}

        # Cosine similarity
        scores = []
        for i, doc_vec in enumerate(self.tf_vectors):
            score = sum(q_vec.get(t, 0) * doc_vec.get(t, 0) for t in q_vec)
            scores.append((score, i))

        scores.sort(reverse=True)
        results = []
        for score, idx in scores[:top_k]:
            chunk = self.chunks[idx].copy()
            chunk["score"] = round(score, 4)
            results.append(chunk)

        return results


# ---------------------------------------------------------------------------
# Book index persistence
# ---------------------------------------------------------------------------

def get_book_id(filepath: str) -> str:
    """Generate a stable ID for a book based on its path and content hash."""
    with open(filepath, "rb") as f:
        content_hash = hashlib.md5(f.read(1024 * 100)).hexdigest()[:8]
    name = Path(filepath).stem
    # Clean name for filesystem
    clean = re.sub(r'[^a-zA-Z0-9_-]', '_', name)[:50]
    return f"{clean}_{content_hash}"


def save_index(book_id: str, metadata: dict, chunks: list[dict]):
    """Save book index to disk."""
    data = {
        "metadata": metadata,
        "chunks": chunks,
    }
    index_path = INDEX_DIR / f"{book_id}.json"
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Index saved: {index_path}")


def load_index(book_id: str) -> tuple[dict, list[dict]] | None:
    """Load book index from disk."""
    index_path = INDEX_DIR / f"{book_id}.json"
    if not index_path.exists():
        return None
    with open(index_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["metadata"], data["chunks"]


def list_indexes() -> list[dict]:
    """List all indexed books."""
    books = []
    for f in INDEX_DIR.glob("*.json"):
        try:
            with open(f, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            meta = data["metadata"]
            meta["chunks"] = len(data["chunks"])
            meta["index_file"] = str(f)
            books.append(meta)
        except Exception:
            continue
    return books


# ---------------------------------------------------------------------------
# Chat history
# ---------------------------------------------------------------------------

def load_history(book_id: str) -> list[dict]:
    """Load chat history for a book."""
    path = HISTORY_DIR / f"{book_id}_history.json"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_history(book_id: str, history: list[dict]):
    """Save chat history for a book."""
    path = HISTORY_DIR / f"{book_id}_history.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Ollama integration
# ---------------------------------------------------------------------------

def check_ollama() -> bool:
    """Check if Ollama is running."""
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


def query_ollama(system_prompt: str, user_message: str, context_chunks: list[dict]) -> str:
    """Send a question with context to Ollama and return the response."""
    # Build context block
    context_parts = []
    for i, chunk in enumerate(context_chunks, 1):
        context_parts.append(
            f"--- Source {i} (relevance: {chunk.get('score', 'N/A')}) ---\n"
            f"{chunk['text'][:2000]}\n"
        )
    context_block = "\n".join(context_parts)

    full_user_message = (
        f"CONTEXT FROM THE BOOK:\n\n{context_block}\n\n"
        f"QUESTION: {user_message}"
    )

    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": full_user_message},
        ],
        "stream": False,
        "options": {
            "temperature": 0.3,
            "num_ctx": 8192,
        },
    }

    try:
        r = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json=payload,
            timeout=120,
        )
        r.raise_for_status()
        return r.json()["message"]["content"]
    except requests.exceptions.ConnectionError:
        return "[Error] Cannot connect to Ollama. Make sure it is running on localhost:11434."
    except requests.exceptions.Timeout:
        return "[Error] Ollama request timed out. The model might be loading or overloaded."
    except Exception as e:
        return f"[Error] Ollama request failed: {e}"


# ---------------------------------------------------------------------------
# Interactive chat
# ---------------------------------------------------------------------------

def run_chat(book_id: str, metadata: dict, chunks: list[dict]):
    """Run the interactive chat loop."""
    title = metadata.get("title", "Unknown")
    filename = metadata.get("filename", "unknown")

    print(f"\n{'='*60}")
    print(f"  Book Agent: {title}")
    print(f"  File: {filename}")
    print(f"  Chunks indexed: {len(chunks)}")
    print(f"  Total words: {sum(c['word_count'] for c in chunks):,}")
    print(f"{'='*60}")
    print()
    print("  Ask questions about the book. Type 'quit' or 'exit' to stop.")
    print("  Type 'history' to see past questions.")
    print("  Type 'sources' after a question to see which chunks were used.")
    print()

    # Build search index
    print("  Building search index...", end=" ", flush=True)
    index = SearchIndex(chunks)
    print("done.\n")

    system_prompt = (
        f"You are a tutor for the book '{title}'. "
        f"Answer questions using ONLY the provided context from the book. "
        f"If the answer is not in the context, say so clearly. "
        f"Be concise but thorough. Quote the book when relevant."
    )

    history = load_history(book_id)
    last_sources = []

    if not check_ollama():
        print("  [Warning] Ollama is not running at localhost:11434.")
        print("  Start it with: ollama serve")
        print("  Then pull the model: ollama pull qwen2.5:7b")
        print()

    while True:
        try:
            question = input("  You> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  Goodbye.")
            break

        if not question:
            continue

        if question.lower() in ("quit", "exit", "q"):
            print("  Goodbye.")
            break

        if question.lower() == "history":
            if not history:
                print("  No chat history yet.\n")
            else:
                print(f"\n  --- Chat History ({len(history)} exchanges) ---")
                for entry in history[-10:]:
                    print(f"  Q: {entry['question'][:80]}")
                    print(f"  A: {entry['answer'][:120]}...")
                    print()
            continue

        if question.lower() == "sources":
            if not last_sources:
                print("  No sources from last query.\n")
            else:
                print(f"\n  --- Sources used ---")
                for i, s in enumerate(last_sources, 1):
                    print(f"  [{i}] Score: {s.get('score', 'N/A')} | {s['heading'][:60]}")
                    preview = s['text'][:200].replace('\n', ' ')
                    print(f"      {preview}...")
                    print()
            continue

        # Search for relevant chunks
        results = index.search(question, top_k=TOP_K)
        last_sources = results

        # Query Ollama
        print("  Thinking...", flush=True)
        answer = query_ollama(system_prompt, question, results)
        print()

        # Wrap and display answer
        wrapped = textwrap.fill(answer, width=76, initial_indent="  ", subsequent_indent="  ")
        print(wrapped)
        print()

        # Save to history
        history.append({
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "answer": answer,
            "sources_used": [
                {"id": r["id"], "score": r.get("score", 0), "heading": r["heading"]}
                for r in results
            ],
        })
        save_history(book_id, history)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Book-to-Agent: Turn books into interactive AI tutors.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
            Examples:
              python3 book_to_agent.py book.pdf
              python3 book_to_agent.py notes.md --index-only
              python3 book_to_agent.py --list
              python3 book_to_agent.py book.pdf --model llama3.1:8b
        """),
    )
    parser.add_argument("file", nargs="?", help="Path to PDF, text, or markdown file")
    parser.add_argument("--index-only", action="store_true", help="Only build the index, don't start chat")
    parser.add_argument("--list", action="store_true", help="List all indexed books")
    parser.add_argument("--model", default=OLLAMA_MODEL, help=f"Ollama model to use (default: {OLLAMA_MODEL})")
    parser.add_argument("--ollama-url", default=OLLAMA_URL, help=f"Ollama API URL (default: {OLLAMA_URL})")
    parser.add_argument("--top-k", type=int, default=TOP_K, help=f"Number of context chunks to retrieve (default: {TOP_K})")

    args = parser.parse_args()

    # Apply overrides
    global OLLAMA_MODEL, OLLAMA_URL, TOP_K
    OLLAMA_MODEL = args.model
    OLLAMA_URL = args.ollama_url
    TOP_K = args.top_k

    # List mode
    if args.list:
        books = list_indexes()
        if not books:
            print("No books indexed yet.")
            print(f"Index directory: {INDEX_DIR}")
            return
        print(f"\nIndexed books ({len(books)}):\n")
        for b in books:
            print(f"  {b.get('title', 'Unknown')}")
            print(f"    File: {b.get('filepath', 'N/A')}")
            print(f"    Chunks: {b.get('chunks', '?')} | Indexed: {b.get('indexed_at', 'N/A')}")
            print()
        return

    # Need a file for index/chat modes
    if not args.file:
        parser.print_help()
        sys.exit(1)

    filepath = os.path.abspath(args.file)
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        sys.exit(1)

    book_id = get_book_id(filepath)
    filename = Path(filepath).name
    title = Path(filepath).stem.replace("_", " ").replace("-", " ").title()

    # Check if already indexed
    cached = load_index(book_id)
    if cached:
        metadata, chunks = cached
        print(f"Loaded existing index for: {title} ({len(chunks)} chunks)")
    else:
        # Extract and chunk
        print(f"Extracting text from: {filename}...")
        text = extract_text_from_file(filepath)

        if not text.strip():
            print("Error: No text could be extracted from this file.")
            sys.exit(1)

        word_count = len(text.split())
        print(f"Extracted {word_count:,} words.")

        print("Chunking text...")
        chunks = chunk_text(text)
        print(f"Created {len(chunks)} chunks.")

        metadata = {
            "title": title,
            "filename": filename,
            "filepath": filepath,
            "word_count": word_count,
            "chunk_count": len(chunks),
            "indexed_at": datetime.now().isoformat(),
        }

        save_index(book_id, metadata, chunks)

    if args.index_only:
        print("Index built. Use without --index-only to start chatting.")
        return

    # Start interactive chat
    run_chat(book_id, metadata, chunks)


if __name__ == "__main__":
    main()
