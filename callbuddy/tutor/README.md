# Book-to-Agent RAG Tutor

Turn any ebook, transcript, or text file into an interactive AI tutor.

No cloud dependencies. No vector databases. Pure Python + optional Ollama.


## Setup

No pip install needed for the core engine. It runs on Python stdlib only.

For the API server:
```bash
pip install fastapi uvicorn
```

For better PDF support (optional):
```bash
pip install pypdf
```


## How to Ingest Books

Drop your .txt, .md, or .pdf files into a folder, then run:

```bash
cd ~/behique/callbuddy/tutor
python3 ingest.py /path/to/your/books/
```

This will:
1. Scan the directory for supported files
2. Extract text and chunk it (1000 chars, 200 overlap)
3. Build a TF-IDF inverted index
4. Save everything to `brain/chunks.json` and `brain/index.json`

Re-run ingest anytime you add new files. It rebuilds from scratch.


## How to Query

### CLI (no dependencies)
```bash
python3 query.py "what is the main argument of the book"
python3 query.py "explain the framework" --top_k 5
```

### API Server
```bash
python3 server.py
# Runs on port 8096

# Query
curl -X POST http://localhost:8096/tutor/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "what is the key takeaway", "top_k": 3}'

# Stats
curl http://localhost:8096/tutor/stats
```

### With Ollama (recommended)
If Ollama is running on localhost:11434 with llama3, the tutor automatically sends retrieved chunks to the model for a synthesized, conversational answer.

Without Ollama, it returns the raw relevant chunks with relevance scores.


## How It Works

1. **Ingest**: Files are chunked with overlap so context isn't lost at boundaries
2. **Index**: TF-IDF (term frequency-inverse document frequency) weights each term per chunk
3. **Search**: Your question is tokenized, matched against the inverted index, scored by cosine similarity
4. **Answer**: Top chunks are either returned raw or sent to Ollama for synthesis


## Business Model

**$20 ebook becomes a $50/mo AI mentorship service.**

The play:
- Buy an ebook or course for $20
- Ingest the full content into this tutor
- Sell access as "AI-powered mentorship" at $50/mo
- The customer gets instant, 24/7 answers from the book's knowledge
- You provide the curation, the packaging, the brand

Stack it:
- Multiple books per niche = deeper knowledge base
- Add your own notes, transcripts, frameworks
- Bundle with community access (Telegram/Discord)
- Upsell 1-on-1 coaching for premium tier

Margins: Near zero cost (self-hosted on Cobo), recurring revenue, scales with content not time.
