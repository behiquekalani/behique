#!/usr/bin/env python3
"""
Book Agent Web UI — Flask server
Turn any book/PDF into an interactive AI tutor. Chat with your books.

Usage:
    pip install flask requests PyPDF2
    python3 app.py
    Open http://localhost:7860

Secrets: OLLAMA_HOST, OLLAMA_MODEL, OPENAI_API_KEY (all via env vars or .env)
"""

import hashlib
import json
import math
import os
import re
import tempfile
import uuid
from collections import Counter
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, render_template_string, request, session

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", os.urandom(24).hex())

# ── CONFIG ───────────────────────────────────────────────────────────────────────
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
FALLBACK_MODEL = os.getenv("FALLBACK_MODEL", "gpt-4o-mini")
CHUNK_TARGET_WORDS = 500
TOP_K = 4
MAX_CONTEXT_CHARS = 4000
DATA_DIR = Path(os.getenv("BOOK_AGENT_DATA", str(Path.home() / ".book_agent")))
DATA_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md", ".markdown", ".rst"}

# In-memory book sessions (reloaded from disk on server restart)
_loaded_books: dict = {}

# ── TEXT EXTRACTION ──────────────────────────────────────────────────────────────
def extract_text(filepath: str) -> str:
    ext = Path(filepath).suffix.lower()
    if ext == ".pdf":
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(filepath)
            pages = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    pages.append(text)
            return "\n\n".join(pages)
        except ImportError:
            return "Error: PyPDF2 not installed. Run: pip install PyPDF2"
        except Exception as e:
            return f"Error reading PDF: {e}"
    else:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            return f.read()


# ── CHUNKING ─────────────────────────────────────────────────────────────────────
def chunk_text(text: str, target_words: int = CHUNK_TARGET_WORDS) -> list[dict]:
    chunks = []
    paragraphs = re.split(r"\n\s*\n", text)
    current = []
    current_words = 0

    for para in paragraphs:
        words = para.split()
        if not words:
            continue
        if current_words + len(words) > target_words and current:
            chunks.append({"text": "\n\n".join(current), "index": len(chunks)})
            current = []
            current_words = 0
        current.append(para)
        current_words += len(words)

    if current:
        chunks.append({"text": "\n\n".join(current), "index": len(chunks)})

    return chunks


# ── TF-IDF SEARCH INDEX ──────────────────────────────────────────────────────────
STOPWORDS = {
    'the','a','an','is','are','was','were','be','been','being','have','has',
    'had','do','does','did','will','would','could','should','may','might',
    'can','to','of','in','for','on','with','at','by','from','as','and',
    'but','or','not','it','its','this','that','these','those','he','she',
    'they','we','you','i','me','my','your','his','her','our','their',
}

class SearchIndex:
    def __init__(self, chunks: list[dict]):
        self.chunks = chunks
        self.idf: dict = {}
        self.tf_vectors: list[dict] = []
        self._build()

    def _tokenize(self, text: str) -> list[str]:
        text = text.lower()
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        return [t for t in text.split() if len(t) > 1 and t not in STOPWORDS]

    def _build(self):
        n = len(self.chunks)
        doc_freq: Counter = Counter()
        tf_raw: list[Counter] = []
        for chunk in self.chunks:
            tokens = self._tokenize(chunk["text"])
            tf = Counter(tokens)
            tf_raw.append(tf)
            for token in set(tokens):
                doc_freq[token] += 1

        for term, df in doc_freq.items():
            self.idf[term] = math.log((n + 1) / (df + 1)) + 1

        for tf in tf_raw:
            vec = {}
            total = sum(tf.values()) or 1
            for term, count in tf.items():
                vec[term] = (count / total) * self.idf.get(term, 1.0)
            norm = math.sqrt(sum(v * v for v in vec.values())) or 1
            self.tf_vectors.append({k: v / norm for k, v in vec.items()})

    def search(self, query: str, top_k: int = TOP_K) -> list[dict]:
        tokens = self._tokenize(query)
        if not tokens:
            return self.chunks[:top_k]

        q_tf = Counter(tokens)
        total = sum(q_tf.values()) or 1
        q_vec = {}
        for term, count in q_tf.items():
            q_vec[term] = (count / total) * self.idf.get(term, 1.0)
        norm = math.sqrt(sum(v * v for v in q_vec.values())) or 1
        q_vec = {k: v / norm for k, v in q_vec.items()}

        scores = [(sum(q_vec.get(t, 0) * vec.get(t, 0) for t in q_vec), i)
                  for i, vec in enumerate(self.tf_vectors)]
        scores.sort(reverse=True)
        return [self.chunks[i] for _, i in scores[:top_k]]


# ── LLM QUERY ────────────────────────────────────────────────────────────────────
def build_prompt(question: str, context_chunks: list[dict], history: list) -> list[dict]:
    context = "\n\n---\n\n".join(c["text"] for c in context_chunks)
    if len(context) > MAX_CONTEXT_CHARS:
        context = context[:MAX_CONTEXT_CHARS] + "..."

    system_msg = (
        "You are a study assistant for this specific book. "
        "Answer questions using ONLY the provided book excerpts. "
        "If the answer is not in the excerpts, say so clearly. "
        "Be specific, cite what you found, and be concise.\n\n"
        f"BOOK EXCERPTS:\n{context}"
    )

    messages = [{"role": "system", "content": system_msg}]
    for h in history[-6:]:
        messages.append({"role": h["role"], "content": h["content"]})
    messages.append({"role": "user", "content": question})
    return messages


def query_llm(messages: list) -> str:
    import requests as req

    # Try Ollama first
    try:
        resp = req.post(
            f"{OLLAMA_HOST}/v1/chat/completions",
            json={"model": OLLAMA_MODEL, "messages": messages, "temperature": 0.3},
            timeout=30,
            headers={"Authorization": "Bearer ollama"},
        )
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"]
    except Exception:
        pass

    # OpenAI fallback
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        try:
            resp = req.post(
                "https://api.openai.com/v1/chat/completions",
                json={"model": FALLBACK_MODEL, "messages": messages, "temperature": 0.3},
                headers={"Authorization": f"Bearer {openai_key}"},
                timeout=30,
            )
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
        except Exception:
            pass

    return "Could not reach any AI model. Make sure Ollama is running (ollama serve) or set OPENAI_API_KEY."


# ── BOOK MANAGEMENT ───────────────────────────────────────────────────────────────
def load_book(filepath: str, filename: str) -> dict:
    """Extract, chunk, and index a book. Returns book metadata."""
    text = extract_text(filepath)
    if text.startswith("Error:"):
        return {"error": text}

    chunks = chunk_text(text)
    index = SearchIndex(chunks)
    book_id = hashlib.md5(text[:500].encode()).hexdigest()[:12]

    book = {
        "id": book_id,
        "filename": filename,
        "chunks": len(chunks),
        "words": len(text.split()),
        "loaded_at": datetime.now().isoformat(),
        "index": index,
        "history": [],
    }

    _loaded_books[book_id] = book
    return {"book_id": book_id, "filename": filename, "chunks": len(chunks), "words": len(text.split())}


# ── ROUTES ────────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route("/api/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file"}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "Empty filename"}), 400

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({"error": f"Unsupported format. Use: {', '.join(ALLOWED_EXTENSIONS)}"}), 400

    # Save to temp file
    tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
    file.save(tmp.name)

    try:
        result = load_book(tmp.name, file.filename)
        return jsonify(result)
    finally:
        os.unlink(tmp.name)


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json or {}
    book_id = data.get("book_id")
    question = (data.get("question") or "").strip()

    if not book_id or not question:
        return jsonify({"error": "Missing book_id or question"}), 400

    book = _loaded_books.get(book_id)
    if not book:
        return jsonify({"error": "Book not found. Please re-upload."}), 404

    # Search for relevant chunks
    results = book["index"].search(question)

    # Build messages and query
    messages = build_prompt(question, results, book["history"])
    answer = query_llm(messages)

    # Track history (last 10 turns)
    book["history"].append({"role": "user", "content": question})
    book["history"].append({"role": "assistant", "content": answer})
    if len(book["history"]) > 20:
        book["history"] = book["history"][-20:]

    return jsonify({
        "answer": answer,
        "chunks_used": len(results),
        "excerpt": results[0]["text"][:200] if results else "",
    })


@app.route("/api/books")
def list_books():
    return jsonify([
        {"id": b["id"], "filename": b["filename"], "chunks": b["chunks"], "words": b["words"]}
        for b in _loaded_books.values()
    ])


# ── HTML TEMPLATE ────────────────────────────────────────────────────────────────
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Book Agent — Chat with your books</title>
<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg: #0a0a0f;
  --surface: #111118;
  --surface2: #1a1a24;
  --border: rgba(255,255,255,0.07);
  --text: #e8e8f0;
  --muted: rgba(232,232,240,0.45);
  --accent: #7c6af7;
  --accent2: #f7a96a;
  --success: #6af79a;
  --radius: 14px;
}

body {
  background: var(--bg);
  color: var(--text);
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Segoe UI', system-ui, sans-serif;
  height: 100vh;
  display: grid;
  grid-template-columns: 280px 1fr;
  grid-template-rows: 60px 1fr;
}

/* NAV */
header {
  grid-column: 1/-1;
  display: flex;
  align-items: center;
  padding: 0 24px;
  border-bottom: 1px solid var(--border);
  background: rgba(10,10,15,0.95);
  backdrop-filter: blur(20px);
  z-index: 10;
}

.logo {
  font-size: 16px;
  font-weight: 700;
  letter-spacing: -0.3px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.logo-icon {
  width: 26px; height: 26px;
  background: linear-gradient(135deg, var(--accent) 0%, var(--accent2) 100%);
  border-radius: 7px;
  display: flex; align-items: center; justify-content: center;
  font-size: 14px;
}

.header-sub {
  font-size: 12px;
  color: var(--muted);
  margin-left: 16px;
  padding-left: 16px;
  border-left: 1px solid var(--border);
}

/* SIDEBAR */
aside {
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  padding: 20px 16px;
  gap: 12px;
  overflow-y: auto;
}

.sidebar-title {
  font-size: 11px;
  font-weight: 600;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.8px;
  margin-bottom: 4px;
}

/* UPLOAD ZONE */
.upload-zone {
  border: 1px dashed rgba(124,106,247,0.3);
  border-radius: var(--radius);
  padding: 20px 12px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  background: rgba(124,106,247,0.03);
}

.upload-zone:hover, .upload-zone.drag-over {
  border-color: var(--accent);
  background: rgba(124,106,247,0.08);
}

.upload-icon { font-size: 24px; margin-bottom: 6px; }
.upload-label { font-size: 12px; color: var(--muted); line-height: 1.4; }
.upload-label strong { color: var(--text); display: block; margin-bottom: 2px; }

#fileInput { display: none; }

/* BOOK LIST */
.book-item {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.book-item:hover { border-color: rgba(255,255,255,0.15); }
.book-item.active { border-color: var(--accent); background: rgba(124,106,247,0.08); }

.book-name {
  font-size: 13px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 4px;
}

.book-meta {
  font-size: 11px;
  color: var(--muted);
}

/* MAIN CHAT */
main {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: var(--muted);
  text-align: center;
  padding: 40px;
}

.chat-empty-icon { font-size: 48px; margin-bottom: 8px; }
.chat-empty h2 { font-size: 20px; font-weight: 600; color: var(--text); letter-spacing: -0.3px; }
.chat-empty p { font-size: 14px; max-width: 320px; line-height: 1.6; }

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.msg {
  display: flex;
  gap: 12px;
  max-width: 780px;
}

.msg.user { flex-direction: row-reverse; align-self: flex-end; }

.msg-avatar {
  width: 32px; height: 32px;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 14px;
  flex-shrink: 0;
}

.msg.user .msg-avatar { background: var(--accent); }
.msg.assistant .msg-avatar { background: var(--surface2); border: 1px solid var(--border); }

.msg-bubble {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 12px 16px;
  font-size: 14px;
  line-height: 1.6;
  max-width: 620px;
}

.msg.user .msg-bubble {
  background: rgba(124,106,247,0.12);
  border-color: rgba(124,106,247,0.2);
}

.msg-bubble p { margin-bottom: 8px; }
.msg-bubble p:last-child { margin-bottom: 0; }
.msg-bubble code {
  background: var(--surface2);
  padding: 1px 5px;
  border-radius: 4px;
  font-family: 'SF Mono', monospace;
  font-size: 12px;
}

.thinking {
  display: flex;
  gap: 5px;
  align-items: center;
  padding: 12px 16px;
}

.thinking span {
  width: 7px; height: 7px;
  background: var(--muted);
  border-radius: 50%;
  animation: pulse 1.4s ease-in-out infinite;
}
.thinking span:nth-child(2) { animation-delay: 0.2s; }
.thinking span:nth-child(3) { animation-delay: 0.4s; }

@keyframes pulse {
  0%, 80%, 100% { opacity: 0.3; transform: scale(0.8); }
  40% { opacity: 1; transform: scale(1); }
}

/* INPUT BAR */
.chat-input-bar {
  padding: 16px 24px;
  border-top: 1px solid var(--border);
  display: flex;
  gap: 10px;
  align-items: flex-end;
}

#chatInput {
  flex: 1;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 12px 16px;
  color: var(--text);
  font-family: inherit;
  font-size: 14px;
  resize: none;
  max-height: 120px;
  outline: none;
  transition: border-color 0.2s;
}

#chatInput:focus { border-color: var(--accent); }
#chatInput::placeholder { color: var(--muted); }

#sendBtn {
  width: 42px; height: 42px;
  background: var(--accent);
  border: none;
  border-radius: 10px;
  color: white;
  font-size: 16px;
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  transition: all 0.2s;
}

#sendBtn:hover { background: #6a58e0; }
#sendBtn:disabled { opacity: 0.4; cursor: not-allowed; }

/* UPLOAD PROGRESS */
.upload-progress {
  display: none;
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 12px;
  font-size: 12px;
}

.progress-bar-wrap {
  background: var(--bg);
  border-radius: 4px;
  height: 4px;
  margin-top: 8px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: var(--accent);
  border-radius: 4px;
  animation: progress 2s ease-in-out infinite;
}

@keyframes progress {
  0% { width: 0%; }
  50% { width: 70%; }
  100% { width: 95%; }
}

/* SCROLLBAR */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }
</style>
</head>
<body>

<header>
  <div class="logo">
    <div class="logo-icon">📚</div>
    Book Agent
  </div>
  <div class="header-sub">Upload any book. Ask anything. Get answers from the text.</div>
</header>

<aside>
  <div class="sidebar-title">Your Books</div>

  <div class="upload-zone" id="uploadZone" onclick="document.getElementById('fileInput').click()">
    <div class="upload-icon">📄</div>
    <div class="upload-label">
      <strong>Drop a book here</strong>
      PDF, Markdown, or text
    </div>
  </div>

  <input type="file" id="fileInput" accept=".pdf,.txt,.md,.markdown,.rst">

  <div class="upload-progress" id="uploadProgress">
    <span id="uploadStatus">Processing book...</span>
    <div class="progress-bar-wrap"><div class="progress-bar"></div></div>
  </div>

  <div id="bookList"></div>
</aside>

<main id="mainArea">
  <div class="chat-empty" id="emptyState">
    <div class="chat-empty-icon">📚</div>
    <h2>Chat with your books</h2>
    <p>Upload a PDF, Markdown, or text file to get started. Ask questions and get answers sourced directly from the text.</p>
  </div>
  <div class="chat-messages" id="chatMessages" style="display:none;"></div>
  <div class="chat-input-bar" id="chatInputBar" style="display:none;">
    <textarea id="chatInput" rows="1" placeholder="Ask anything about this book..."
              onkeydown="handleKey(event)" oninput="autoResize(this)"></textarea>
    <button id="sendBtn" onclick="sendMessage()">↑</button>
  </div>
</main>

<script>
let currentBookId = null;
let isLoading = false;

// ── DRAG & DROP ──────────────────────────────────────────────────────────────
const uploadZone = document.getElementById('uploadZone');
const fileInput = document.getElementById('fileInput');

uploadZone.addEventListener('dragover', e => {
  e.preventDefault();
  uploadZone.classList.add('drag-over');
});

uploadZone.addEventListener('dragleave', () => uploadZone.classList.remove('drag-over'));

uploadZone.addEventListener('drop', e => {
  e.preventDefault();
  uploadZone.classList.remove('drag-over');
  const file = e.dataTransfer.files[0];
  if (file) uploadFile(file);
});

fileInput.addEventListener('change', () => {
  if (fileInput.files[0]) uploadFile(fileInput.files[0]);
});

// ── UPLOAD ───────────────────────────────────────────────────────────────────
async function uploadFile(file) {
  const prog = document.getElementById('uploadProgress');
  const status = document.getElementById('uploadStatus');
  prog.style.display = 'block';
  status.textContent = `Processing "${file.name}"...`;

  const formData = new FormData();
  formData.append('file', file);

  try {
    const resp = await fetch('/api/upload', { method: 'POST', body: formData });
    const data = await resp.json();

    if (data.error) {
      status.textContent = `Error: ${data.error}`;
      setTimeout(() => prog.style.display = 'none', 3000);
      return;
    }

    prog.style.display = 'none';
    addBookToSidebar(data);
    selectBook(data.book_id, data.filename);

  } catch (err) {
    status.textContent = `Upload failed: ${err.message}`;
    setTimeout(() => prog.style.display = 'none', 3000);
  }
}

function addBookToSidebar(data) {
  const list = document.getElementById('bookList');
  const existing = document.getElementById(`book-${data.book_id}`);
  if (existing) return;

  const el = document.createElement('div');
  el.className = 'book-item';
  el.id = `book-${data.book_id}`;
  el.innerHTML = `
    <div class="book-name">${escapeHtml(data.filename)}</div>
    <div class="book-meta">${data.chunks} chunks · ${(data.words/1000).toFixed(1)}k words</div>
  `;
  el.onclick = () => selectBook(data.book_id, data.filename);
  list.appendChild(el);
}

function selectBook(bookId, filename) {
  currentBookId = bookId;

  // Update sidebar
  document.querySelectorAll('.book-item').forEach(el => el.classList.remove('active'));
  const el = document.getElementById(`book-${bookId}`);
  if (el) el.classList.add('active');

  // Show chat UI
  document.getElementById('emptyState').style.display = 'none';
  document.getElementById('chatMessages').style.display = 'flex';
  document.getElementById('chatInputBar').style.display = 'flex';

  // Clear messages and add welcome
  const msgs = document.getElementById('chatMessages');
  msgs.innerHTML = '';
  addMessage('assistant', `📚 **${escapeHtml(filename)}** loaded.\n\nAsk me anything about this book. I'll find the relevant passages and answer from the text.`);

  document.getElementById('chatInput').focus();
}

// ── CHAT ─────────────────────────────────────────────────────────────────────
async function sendMessage() {
  if (isLoading || !currentBookId) return;

  const input = document.getElementById('chatInput');
  const question = input.value.trim();
  if (!question) return;

  input.value = '';
  autoResize(input);

  addMessage('user', question);
  showThinking();
  isLoading = true;
  document.getElementById('sendBtn').disabled = true;

  try {
    const resp = await fetch('/api/chat', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ book_id: currentBookId, question }),
    });

    const data = await resp.json();
    hideThinking();

    if (data.error) {
      addMessage('assistant', `Error: ${data.error}`);
    } else {
      addMessage('assistant', data.answer);
    }

  } catch (err) {
    hideThinking();
    addMessage('assistant', `Network error: ${err.message}`);
  } finally {
    isLoading = false;
    document.getElementById('sendBtn').disabled = false;
    document.getElementById('chatInput').focus();
  }
}

function addMessage(role, text) {
  const msgs = document.getElementById('chatMessages');
  const div = document.createElement('div');
  div.className = `msg ${role}`;
  const avatar = role === 'user' ? '👤' : '📚';
  div.innerHTML = `
    <div class="msg-avatar">${avatar}</div>
    <div class="msg-bubble">${formatText(text)}</div>
  `;
  msgs.appendChild(div);
  msgs.scrollTop = msgs.scrollHeight;
}

let thinkingEl = null;
function showThinking() {
  const msgs = document.getElementById('chatMessages');
  thinkingEl = document.createElement('div');
  thinkingEl.className = 'msg assistant';
  thinkingEl.innerHTML = `
    <div class="msg-avatar">📚</div>
    <div class="msg-bubble thinking">
      <span></span><span></span><span></span>
    </div>
  `;
  msgs.appendChild(thinkingEl);
  msgs.scrollTop = msgs.scrollHeight;
}

function hideThinking() {
  if (thinkingEl) { thinkingEl.remove(); thinkingEl = null; }
}

// ── UTILS ────────────────────────────────────────────────────────────────────
function handleKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
}

function autoResize(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 120) + 'px';
}

function escapeHtml(str) {
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

function formatText(text) {
  // Basic markdown-ish formatting
  text = escapeHtml(text);
  text = text.replace(/[*][*](.*?)[*][*]/g, '<strong>$1</strong>');
  text = text.replace(/[*](.*?)[*]/g, '<em>$1</em>');
  text = text.replace(/`(.*?)`/g, '<code>$1</code>');
  text = text.replace(/\n\n/g, '</p><p>');
  text = text.replace(/\n/g, '<br>');
  return `<p>${text}</p>`;
}

// Load existing books on page load
fetch('/api/books').then(r => r.json()).then(books => {
  books.forEach(b => addBookToSidebar(b));
});
</script>
</body>
</html>"""


if __name__ == "__main__":
    port = int(os.getenv("PORT", 7860))
    print(f"\n📚 Book Agent running at http://localhost:{port}")
    print(f"   Ollama: {OLLAMA_HOST} ({OLLAMA_MODEL})")
    print(f"   Data:   {DATA_DIR}")
    print("\n   Drag a PDF or text file to start chatting with your books.\n")
    app.run(host="0.0.0.0", port=port, debug=False)
