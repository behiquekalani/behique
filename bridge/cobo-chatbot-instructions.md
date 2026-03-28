# Cobo Task: Behike Store Chatbot API

Build a chatbot API that serves the Behike store chat widget. The widget on the website will POST to this server, and Cobo will respond using Ollama with llama3.2.

---

## Setup

Server runs on Cobo at `0.0.0.0:9877`.

### Requirements

```bash
pip install fastapi uvicorn httpx slowapi
```

---

## Full Code: `behike_chat_api.py`

```python
import time
import httpx
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone

app = FastAPI(title="Behike Chat API")

# Rate limiting: 10 requests per minute per IP
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"error": "Too many requests. Try again in a minute."}
    )

# CORS - open for now, lock down later
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ollama config
OLLAMA_URL = "http://localhost:11434"
MODEL = "llama3.2"

SYSTEM_PROMPT = """You are Behike AI, the helpful assistant for the Behike digital products store. You are friendly, concise, and knowledgeable about the following products:

1. AI Employee Guide ($19.99) - A 20-chapter blueprint for building a multi-machine AI system. Covers setup, orchestration, automation, and scaling AI across multiple computers.

2. Personal Budget Template ($9.99) - A spreadsheet template to track spending, set financial goals, and stay on budget. Clean design, easy to customize.

3. Shopify Theme Bundle ($69.99) - All 3 Behike Shopify themes (Starter, Pro, Empire) bundled together at a discount.

4. Behike Starter Theme ($14.99) - A clean, minimal Shopify theme. Perfect for new stores that want a professional look without complexity.

5. Behike Pro Theme ($29.99) - A dark, sleek, conversion-optimized Shopify theme. Built for stores that want to look premium.

6. Behike Empire Theme ($49.99) - A black and gold luxury Shopify theme. For brands that want to make a statement.

All products are sold via Gumroad. The store is built by Kalani Andre, a computer engineering student in Puerto Rico.

Rules:
- Keep responses short (2-3 sentences max).
- Be helpful and direct. No filler.
- If someone asks about something you don't know, say so honestly.
- If asked about pricing, always give the exact price.
- For purchase links, tell them to check the product page on the store.
- Do not make up features or details that are not listed above.
- You can recommend products based on what the user describes they need.
"""

# In-memory session storage (not persistent)
sessions = {}

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = []
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    timestamp: str


@app.get("/health")
async def health():
    """Health check endpoint."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(f"{OLLAMA_URL}/api/tags")
            if r.status_code == 200:
                return {"status": "ok", "model": MODEL}
    except Exception:
        pass
    return {"status": "degraded", "model": MODEL, "note": "Ollama may be unavailable"}


@app.post("/chat", response_model=ChatResponse)
@limiter.limit("10/minute")
async def chat(request: Request, body: ChatRequest):
    """Chat endpoint. Accepts a message and optional history."""

    # Count conversation turns from history
    user_turns = sum(1 for m in (body.history or []) if m.role == "user")

    # After 3 turns, suggest Instagram DM
    if user_turns >= 3:
        return ChatResponse(
            response="I've enjoyed chatting! For more detailed questions, DM us on Instagram @behikeai and Kalani will get back to you personally.",
            timestamp=datetime.now(timezone.utc).isoformat()
        )

    # Build messages for Ollama
    ollama_messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Add history
    for msg in (body.history or []):
        ollama_messages.append({"role": msg.role, "content": msg.content})

    # Add current message
    ollama_messages.append({"role": "user", "content": body.message})

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(
                f"{OLLAMA_URL}/api/chat",
                json={
                    "model": MODEL,
                    "messages": ollama_messages,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 200,
                    }
                }
            )
            r.raise_for_status()
            data = r.json()
            reply = data.get("message", {}).get("content", "Sorry, something went wrong.")

    except httpx.TimeoutException:
        reply = "I'm taking too long to think. Try again in a moment."
    except Exception as e:
        reply = "Something went wrong on my end. DM us on Instagram @behikeai if you need help."

    return ChatResponse(
        response=reply,
        timestamp=datetime.now(timezone.utc).isoformat()
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9877)
```

---

## How to Run

```bash
# Make sure Ollama is running with llama3.2
ollama pull llama3.2

# Run the API
python behike_chat_api.py
```

Or with uvicorn directly:

```bash
uvicorn behike_chat_api:app --host 0.0.0.0 --port 9877
```

---

## Test It

```bash
# Health check
curl http://localhost:9877/health

# Send a chat message
curl -X POST http://localhost:9877/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What products do you have?", "history": []}'
```

---

## Notes

- The widget on the store will POST to `http://192.168.0.151:9877/chat`
- CORS is wide open for now. Once the Cloudflare tunnel is set up, lock it down to the store domain only.
- Rate limit is 10 requests per minute per IP. The widget also has a client-side 2-second cooldown.
- After 3 conversation turns, the bot redirects to Instagram DMs. This keeps Cobo's resources light.
- Sessions are in-memory only. They reset when the server restarts. That's fine for now.
- The `num_predict: 200` option keeps responses short so the bot doesn't ramble.
