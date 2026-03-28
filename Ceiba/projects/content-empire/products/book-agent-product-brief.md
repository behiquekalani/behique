# Book Agent - Product Brief

**Tagline:** Upload any book. Chat with it.

**Status:** Prototype built (CLI tool at `~/behique/tools/book_to_agent.py`)

---

## What It Does

Users upload a book (PDF, text, markdown) and get an AI tutor that answers questions using only that book's content. No hallucination, no generic answers. Just the book.

Use cases:
- Students studying textbooks
- Professionals reading technical manuals
- Book clubs discussing a novel
- Researchers extracting insights from papers
- Language learners working through foreign-language books

---

## How It Works

1. User uploads a book
2. System extracts text, splits into smart chunks (by chapter or ~500 words)
3. TF-IDF index built for fast retrieval (no GPU needed)
4. User asks questions in a chat interface
5. System finds the 3 most relevant chunks and sends them to the LLM
6. LLM answers using ONLY the book content, with source citations

---

## Pricing

| Tier | Books | Questions | Price |
|------|-------|-----------|-------|
| Free | 1 | 10/day | $0 |
| Pro | Unlimited | Unlimited | $9.99/month |
| Team | Unlimited + shared library | Unlimited + collaboration | $29.99/month |

---

## Competitive Landscape

| Competitor | Model | Cost Structure | Our Advantage |
|-----------|-------|---------------|---------------|
| ChatPDF | Cloud APIs (OpenAI) | Expensive per query | We run local = $0 marginal cost |
| BookAI | Cloud APIs | Expensive per query | Same |
| NotebookLM | Google | Free but limited, Google lock-in | Self-hosted, no vendor lock |
| Generic ChatGPT | Cloud API | No book-specific grounding | We ground answers in the actual text |

**Our edge:** Self-hosted Ollama on Cobo (GTX 1080 Ti, 11GB VRAM). Zero API costs. Every query is pure profit after the $9.99 subscription.

---

## Infrastructure

- **Prototype:** Python CLI tool, runs anywhere
- **Production host:** Cobo (GTX 1080 Ti for fast Ollama inference)
- **Stack:** Python backend, simple web frontend (React or plain HTML), Ollama for inference
- **Storage:** JSON indexes on disk (upgrade to SQLite or Postgres later)
- **PDF parsing:** PyPDF2 (lightweight, no heavy deps)
- **Search:** TF-IDF (no embeddings needed for v1, upgrade to embeddings later for better accuracy)

---

## Roadmap

### v1 - CLI Tool (DONE)
- [x] PDF + text + markdown support
- [x] Smart chunking (chapter detection + word-count fallback)
- [x] TF-IDF search index
- [x] Ollama integration (qwen2.5:7b)
- [x] Chat history per book
- [x] Source attribution

### v2 - Web Interface
- [ ] Simple upload page
- [ ] Chat UI (websocket for streaming)
- [ ] User accounts (email + password)
- [ ] Stripe integration for Pro tier
- [ ] Host on Cobo behind Caddy reverse proxy

### v3 - Better Intelligence
- [ ] Sentence-level embeddings (upgrade from TF-IDF)
- [ ] Multi-book queries ("compare what Book A and Book B say about X")
- [ ] Highlights and annotations
- [ ] Export study notes as markdown
- [ ] EPUB support

### v4 - Scale
- [ ] Multi-tenant architecture
- [ ] Rate limiting per tier
- [ ] CDN for static assets
- [ ] Monitoring and analytics
- [ ] Mobile-friendly PWA

---

## Revenue Projections (Conservative)

| Month | Free Users | Pro Users | MRR |
|-------|-----------|-----------|-----|
| 1 | 50 | 5 | $50 |
| 3 | 200 | 20 | $200 |
| 6 | 500 | 50 | $500 |
| 12 | 2,000 | 200 | $2,000 |

Break-even: ~5 Pro subscribers covers Cobo electricity. Everything after that is margin.

---

## Why This Wins

1. **Zero marginal cost.** Cloud competitors pay per API call. We run local.
2. **Privacy.** Books never leave the user's control (self-hosted option).
3. **Speed.** Cobo with 1080 Ti gives fast inference. No cold starts.
4. **Simple.** Upload. Chat. That's it. No learning curve.
5. **Extensible.** Same engine powers the AI Marketplace book vendor NPC.

---

## Connection to Behique Ecosystem

- Feeds into the **AI Marketplace** as a "Book Vendor" NPC
- Powered by **Cobo** (dedicated GPU server)
- Can be offered through **Gumroad** as a one-time purchase (self-hosted version)
- Content about it feeds the **Instagram/content pipeline** (demo videos, tutorials)
- Uses the same Ollama infrastructure as **BehiqueBot**
