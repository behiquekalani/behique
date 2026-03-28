# How to Add an AI Chatbot to Your Website in 30 Minutes

**By Behike**

---

Copyright 2026 Behike. All rights reserved.

No part of this guide may be reproduced, distributed, or transmitted in any form without prior written permission from the author.

**AI Disclosure:** This guide was written with the assistance of AI tools. All code has been tested and verified on real hardware. The system described in this guide was built and deployed by the author before this guide was written. You are getting a proven, working setup.

---

## Chapter 1: What You're Building

By the end of this guide, you will have a floating chat bubble on your website that answers customer questions using AI. It looks like the chat widgets you see on professional SaaS products, the ones that slide up from the corner of the screen.

Here is what makes this different from every other chatbot tutorial.

This one runs on YOUR computer. Not OpenAI's servers. Not a $50/month chatbot service. Your machine, your data, your AI. The monthly cost after setup is $0.

The system has three parts:

1. **Ollama** runs the AI model on your computer.
2. **A Python server** connects your website to Ollama.
3. **A JavaScript widget** gives your visitors a clean chat interface.

It works with any website. WordPress, Shopify, Squarespace, a plain HTML file, anything where you can add a script tag. If you can paste code before `</body>`, you can run this.

Your visitors type a question. The widget sends it to your server. Your server asks the AI. The AI responds. The answer appears in the chat. The whole round trip takes 2-5 seconds depending on your hardware.

---

## Chapter 2: Prerequisites

Before you start, make sure you have these:

**Hardware:**
- A computer with at least 8GB of RAM (16GB recommended)
- Mac, Linux, or Windows all work
- At least 5GB of free disk space for the AI model

**Software:**
- Python 3.8 or newer (check with `python3 --version`)
- A terminal (Terminal on Mac, PowerShell on Windows, any terminal on Linux)
- A text editor (VS Code, Notepad++, whatever you use)

**Access:**
- A website you can edit the HTML of
- The ability to add a `<script>` tag to your pages

**Optional but helpful:**
- Basic familiarity with the command line
- Node.js (only if you want to use PM2 for deployment later)

You do NOT need:
- An OpenAI API key
- A cloud server
- Any prior AI experience

---

## Chapter 3: Install Ollama

Ollama is the engine that runs AI models on your computer. One install, one command, and you have a local AI ready to go.

### Mac

Open Terminal and run:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Or download the app from [ollama.com](https://ollama.com) and drag it to Applications.

### Linux

Same one-liner:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Windows

Download the installer from [ollama.com](https://ollama.com) and run it. Follow the prompts.

### Pull a Model

Now download the AI model. Open a terminal and run:

```bash
ollama pull llama3.2
```

This downloads the llama3.2 model (~2GB). It is the best balance of speed and quality for chatbot use.

**If your computer is slow or has less than 8GB RAM**, use the smaller model instead:

```bash
ollama pull tinyllama
```

Tinyllama is faster but less accurate. Good enough for simple customer questions.

### Test It

Make sure Ollama is running, then test with curl:

```bash
curl http://localhost:11434/api/chat -d '{
  "model": "llama3.2",
  "messages": [{"role": "user", "content": "Say hello"}],
  "stream": false
}'
```

You should see a JSON response with the AI's reply. If you get a "connection refused" error, Ollama is not running. On Mac, open the Ollama app. On Linux, run `ollama serve` in a separate terminal window.

**Expected output:**

```json
{
  "model": "llama3.2",
  "message": {
    "role": "assistant",
    "content": "Hello! How can I help you today?"
  }
}
```

If you see something like that, you are good. Move on.

---

## Chapter 4: Build the Chat API

This Python server sits between your website and Ollama. Your website sends questions to this server. This server asks Ollama. Ollama responds. The server sends the answer back to your website.

### Install Dependencies

```bash
pip install fastapi uvicorn httpx slowapi
```

### Create the Server

Create a new file called `chat_api.py` and paste this entire code block:

```python
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

app = FastAPI(title="Chat API")

# Rate limiting: 10 requests per minute per visitor
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"error": "Too many requests. Try again in a minute."}
    )

# CORS - allows your website to talk to this server
# Replace "*" with your domain in production (e.g. "https://yoursite.com")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ollama settings
OLLAMA_URL = "http://localhost:11434"
MODEL = "llama3.2"  # Change to "tinyllama" if using weaker hardware

# ============================================
# CUSTOMIZE THIS SYSTEM PROMPT FOR YOUR BUSINESS
# ============================================
SYSTEM_PROMPT = """You are a helpful customer service assistant for [YOUR BUSINESS NAME].

You help customers with questions about [YOUR PRODUCTS/SERVICES].

Key information:
- [Product 1]: [Price] - [One sentence description]
- [Product 2]: [Price] - [One sentence description]
- [Product 3]: [Price] - [One sentence description]

Rules:
- Keep responses short (2-3 sentences max).
- Be helpful and direct. No filler.
- If you do not know the answer, say so honestly.
- Never make up information.
"""

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = []

class ChatResponse(BaseModel):
    response: str
    timestamp: str

@app.get("/health")
async def health():
    """Health check. Hit this URL to verify the server is running."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(f"{OLLAMA_URL}/api/tags")
            if r.status_code == 200:
                return {"status": "ok", "model": MODEL}
    except Exception:
        pass
    return {"status": "degraded", "note": "Ollama may be unavailable"}

@app.post("/chat", response_model=ChatResponse)
@limiter.limit("10/minute")
async def chat(request: Request, body: ChatRequest):
    """Main chat endpoint. Receives a message, returns an AI response."""

    # Build the conversation for Ollama
    ollama_messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for msg in (body.history or []):
        ollama_messages.append({"role": msg.role, "content": msg.content})

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
        reply = "I'm taking a moment to think. Please try again."
    except Exception:
        reply = "Something went wrong. Please try again later."

    return ChatResponse(
        response=reply,
        timestamp=datetime.now(timezone.utc).isoformat()
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9877)
```

### Start the Server

```bash
python chat_api.py
```

You should see output like:

```
INFO:     Uvicorn running on http://0.0.0.0:9877
```

Test it:

```bash
curl -X POST http://localhost:9877/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What products do you sell?", "history": []}'
```

If you get a JSON response with the AI's answer, your server is working. Leave it running and move to the next chapter.

---

## Chapter 5: Add the Chat Widget

This is the JavaScript code that creates the floating chat bubble on your website. It handles the UI, sends messages to your server, and displays responses.

### The Widget Code

Create a file called `chat-widget.js` and paste this code:

```javascript
(function() {
  // ============================================
  // CONFIGURE THESE THREE THINGS
  // ============================================
  const API_URL = 'http://localhost:9877';  // Your server address
  const GREETING = "Hey! Ask me anything."; // First message visitors see
  const BOT_NAME = "AI Assistant";          // Name shown in chat header

  const RATE_LIMIT_MS = 2000;
  const SESSION_KEY = 'chat-history';
  let isOpen = false;
  let lastSendTime = 0;
  let isWaiting = false;

  function loadHistory() {
    try {
      const saved = sessionStorage.getItem(SESSION_KEY);
      return saved ? JSON.parse(saved) : [{ role: 'assistant', content: GREETING }];
    } catch (e) {
      return [{ role: 'assistant', content: GREETING }];
    }
  }

  function saveHistory(messages) {
    try { sessionStorage.setItem(SESSION_KEY, JSON.stringify(messages)); } catch (e) {}
  }

  let messages = loadHistory();

  function createWidget() {
    const widget = document.createElement('div');
    widget.id = 'ai-chat';
    widget.innerHTML = `
      <style>
        #ai-chat-toggle {
          position: fixed; bottom: 24px; right: 24px; z-index: 9999;
          width: 48px; height: 48px; border-radius: 50%;
          background: #0A84FF; border: none; cursor: pointer;
          display: flex; align-items: center; justify-content: center;
          font-size: 22px; box-shadow: 0 4px 20px rgba(0,0,0,0.4);
          transition: transform 0.2s;
        }
        #ai-chat-toggle:hover { transform: scale(1.1); }
        #ai-chat-panel {
          position: fixed; bottom: 84px; right: 24px; z-index: 9998;
          width: 320px; height: 450px;
          background: rgba(20,20,20,0.95);
          backdrop-filter: blur(20px);
          border-radius: 16px;
          border: 1px solid rgba(255,255,255,0.1);
          box-shadow: 0 8px 40px rgba(0,0,0,0.6);
          display: none; flex-direction: column; overflow: hidden;
        }
        #ai-chat-panel.open { display: flex; }
        .chat-header {
          display: flex; align-items: center; justify-content: space-between;
          padding: 14px 16px;
          border-bottom: 1px solid rgba(255,255,255,0.08);
        }
        .chat-header-title {
          font-size: 15px; font-weight: 600; color: #F5F5F7;
          font-family: -apple-system, sans-serif;
        }
        .chat-close {
          background: none; border: none; color: #86868B;
          font-size: 18px; cursor: pointer; padding: 2px 6px;
          border-radius: 6px;
        }
        .chat-messages {
          flex: 1; overflow-y: auto; padding: 16px;
          display: flex; flex-direction: column; gap: 12px;
        }
        .chat-msg {
          max-width: 85%; padding: 10px 14px; border-radius: 14px;
          font-size: 13px; line-height: 1.5;
          font-family: -apple-system, sans-serif; word-wrap: break-word;
        }
        .chat-msg.assistant {
          background: rgba(255,255,255,0.08); color: #F5F5F7;
          align-self: flex-start; border-bottom-left-radius: 4px;
        }
        .chat-msg.user {
          background: #0A84FF; color: #fff;
          align-self: flex-end; border-bottom-right-radius: 4px;
        }
        .chat-msg.error {
          background: rgba(255,59,48,0.15); color: #FF6961;
          align-self: flex-start;
        }
        .chat-typing { display: none; gap: 4px; padding: 10px 14px;
          background: rgba(255,255,255,0.08); border-radius: 14px;
          align-self: flex-start; }
        .chat-typing.visible { display: flex; }
        .chat-typing-dot {
          width: 6px; height: 6px; background: #86868B;
          border-radius: 50%; animation: bounce 1.2s infinite;
        }
        .chat-typing-dot:nth-child(2) { animation-delay: 0.2s; }
        .chat-typing-dot:nth-child(3) { animation-delay: 0.4s; }
        @keyframes bounce {
          0%,60%,100% { transform: translateY(0); opacity: 0.4; }
          30% { transform: translateY(-4px); opacity: 1; }
        }
        .chat-input-area {
          display: flex; gap: 8px; padding: 12px 16px;
          border-top: 1px solid rgba(255,255,255,0.08);
        }
        .chat-input {
          flex: 1; padding: 10px 14px;
          background: rgba(255,255,255,0.06);
          border: 1px solid rgba(255,255,255,0.1);
          border-radius: 980px; color: #F5F5F7; font-size: 13px;
          outline: none; font-family: -apple-system, sans-serif;
        }
        .chat-input::placeholder { color: #86868B; }
        .chat-input:focus { border-color: #0A84FF; }
        .chat-send {
          background: #0A84FF; border: none; color: #fff;
          width: 36px; height: 36px; border-radius: 50%;
          cursor: pointer; display: flex; align-items: center;
          justify-content: center;
        }
        .chat-send:disabled { opacity: 0.4; cursor: default; }
        .chat-send svg { width: 16px; height: 16px; fill: #fff; }
        @media (max-width: 480px) {
          #ai-chat-panel { left: 12px; right: 12px; bottom: 78px;
            width: auto; height: 400px; }
        }
      </style>
      <button id="ai-chat-toggle">💬</button>
      <div id="ai-chat-panel">
        <div class="chat-header">
          <span class="chat-header-title">${BOT_NAME}</span>
          <button class="chat-close">&times;</button>
        </div>
        <div class="chat-messages" id="chatMessages"></div>
        <div class="chat-typing" id="chatTyping">
          <div class="chat-typing-dot"></div>
          <div class="chat-typing-dot"></div>
          <div class="chat-typing-dot"></div>
        </div>
        <div class="chat-input-area">
          <input type="text" class="chat-input" id="chatInput"
            placeholder="Ask something..." autocomplete="off">
          <button class="chat-send" id="chatSend">
            <svg viewBox="0 0 24 24">
              <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
            </svg>
          </button>
        </div>
      </div>`;
    document.body.appendChild(widget);

    const toggle = document.getElementById('ai-chat-toggle');
    const panel = document.getElementById('ai-chat-panel');
    const closeBtn = panel.querySelector('.chat-close');
    const messagesEl = document.getElementById('chatMessages');
    const typingEl = document.getElementById('chatTyping');
    const inputEl = document.getElementById('chatInput');
    const sendBtn = document.getElementById('chatSend');

    function renderMessages() {
      messagesEl.innerHTML = '';
      messages.forEach(m => appendDOM(m.role, m.content));
      scrollBottom();
    }
    function appendDOM(role, content) {
      const div = document.createElement('div');
      div.className = 'chat-msg ' + role;
      div.textContent = content;
      messagesEl.appendChild(div);
    }
    function scrollBottom() { messagesEl.scrollTop = messagesEl.scrollHeight; }
    function showTyping(show) {
      typingEl.classList.toggle('visible', show);
      if (show) { messagesEl.appendChild(typingEl); scrollBottom(); }
    }

    async function sendMessage() {
      const text = inputEl.value.trim();
      if (!text || isWaiting) return;
      if (Date.now() - lastSendTime < RATE_LIMIT_MS) return;
      lastSendTime = Date.now();

      messages.push({ role: 'user', content: text });
      appendDOM('user', text);
      inputEl.value = '';
      scrollBottom();
      saveHistory(messages);

      isWaiting = true;
      sendBtn.disabled = true;
      showTyping(true);

      try {
        const res = await fetch(API_URL + '/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: text, history: messages.slice(0, -1) })
        });
        if (!res.ok) throw new Error('Server error');
        const data = await res.json();
        const reply = data.response || 'Sorry, something went wrong.';
        messages.push({ role: 'assistant', content: reply });
        showTyping(false);
        appendDOM('assistant', reply);
      } catch (e) {
        showTyping(false);
        messages.push({ role: 'error', content: 'Chat is offline. Try again later.' });
        appendDOM('error', 'Chat is offline. Try again later.');
      }
      scrollBottom();
      saveHistory(messages);
      isWaiting = false;
      sendBtn.disabled = false;
      inputEl.focus();
    }

    toggle.addEventListener('click', () => {
      isOpen = !isOpen;
      panel.classList.toggle('open', isOpen);
      if (isOpen) { inputEl.focus(); scrollBottom(); }
    });
    closeBtn.addEventListener('click', () => {
      isOpen = false; panel.classList.remove('open');
    });
    sendBtn.addEventListener('click', sendMessage);
    inputEl.addEventListener('keydown', e => {
      if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
    });
    document.addEventListener('click', e => {
      if (isOpen && !panel.contains(e.target) && !toggle.contains(e.target)) {
        isOpen = false; panel.classList.remove('open');
      }
    });
    renderMessages();
  }

  document.addEventListener('DOMContentLoaded', createWidget);
})();
```

### Add It to Your Website

Open your website's HTML file. Find the `</body>` tag. Paste this line right before it:

```html
<script src="chat-widget.js"></script>
```

If your server is not on the same machine as your website, you need to change `API_URL` in the widget code to point to your server's IP address and port. For example: `http://192.168.0.100:9877`.

### What Each Part Does

- **API_URL**: Where the widget sends messages. Change this to your server's address.
- **GREETING**: The first message visitors see when they open the chat.
- **BOT_NAME**: The name shown in the chat header.
- **RATE_LIMIT_MS**: Minimum time between messages (prevents spam).
- **sessionStorage**: Saves chat history so it persists while the tab is open.

The widget creates a floating blue circle in the bottom-right corner. Click it and a chat panel slides up. Messages appear in speech bubbles. There is a typing indicator with animated dots while the AI thinks.

---

## Chapter 6: Customize for Your Business

The most important customization is the system prompt. This is the instruction you give the AI that tells it who it is, what it knows, and how to behave. A good system prompt is the difference between a useful chatbot and a useless one.

### How to Write a Good System Prompt

Follow this formula:

1. **Identity**: Tell the AI who it is ("You are the customer support bot for...")
2. **Knowledge**: List the specific information it should know (products, prices, policies)
3. **Rules**: Tell it how to behave (keep answers short, never make things up, etc.)

The more specific information you put in, the better the answers will be.

### Example 1: Ecommerce Store

```python
SYSTEM_PROMPT = """You are the helpful assistant for GlowSkin Beauty.

Products we sell:
- Vitamin C Serum ($24.99) - Brightening serum for all skin types
- Retinol Night Cream ($34.99) - Anti-aging cream, use at night only
- SPF 50 Daily Moisturizer ($19.99) - Lightweight, no white cast
- Hydrating Face Mask ($12.99) - Use 2-3 times per week

Shipping: Free over $50. Standard shipping is $4.99, takes 3-5 business days.
Returns: 30-day return policy, item must be unopened.

Rules:
- Keep responses to 2-3 sentences.
- Always mention the exact price when discussing a product.
- If someone asks about ingredients, tell them to check the product page.
- Never recommend products for medical conditions.
"""
```

### Example 2: Freelancer Portfolio

```python
SYSTEM_PROMPT = """You are the assistant on Alex Rivera's portfolio website.

Alex is a freelance web designer based in Austin, TX. He builds websites for small businesses and startups.

Services:
- Landing Page Design ($1,500) - Single page, mobile responsive, 2-week turnaround
- Full Website (from $3,000) - Multi-page site, CMS included, 4-6 week turnaround
- Brand Identity Package ($2,000) - Logo, colors, typography, brand guide

Availability: Currently booking projects for next month.
Contact: alex@example.com

Rules:
- Be professional but friendly.
- If someone asks for a quote, tell them to email Alex with project details.
- Keep responses short and helpful.
"""
```

### Example 3: Restaurant

```python
SYSTEM_PROMPT = """You are the virtual assistant for Casa Luna, a Mexican restaurant in Miami.

Hours: Tuesday-Sunday 11am-10pm. Closed Mondays.
Location: 1234 Coral Way, Miami, FL 33145
Phone: (305) 555-0199
Reservations: Call or book on OpenTable.

Popular dishes: Birria tacos ($14), Mole enchiladas ($16), Churros ($8)
We do catering for groups of 20+. Contact us for custom menus.
Parking: Free lot behind the building.

Rules:
- Keep answers short and helpful.
- Always mention hours if someone asks about visiting.
- For dietary restrictions, tell them to call ahead so the chef can prepare.
"""
```

### Adding More Knowledge

The AI can only answer questions about what you put in the system prompt. If customers keep asking about something and the bot cannot answer, add that information to your system prompt and restart the server.

You can also include FAQ-style entries:

```
Common questions:
Q: Do you ship internationally? A: Not yet, US only for now.
Q: Can I cancel my order? A: Yes, within 1 hour of placing it. Email us.
Q: Do you offer discounts? A: Sign up for our newsletter for 10% off your first order.
```

---

## Chapter 7: Deploy It

You have three options for keeping your chatbot running.

### Option A: Run on Your Own Computer

Best for: testing, local businesses, or if your computer is always on.

Just keep the terminal window open with `python chat_api.py` running. The downside is that if your computer sleeps, shuts down, or restarts, the chatbot goes offline.

For a more reliable setup on Mac/Linux, use a process manager:

```bash
# Install PM2 (requires Node.js)
npm install -g pm2

# Start the server with PM2
pm2 start chat_api.py --interpreter python3 --name chatbot

# Make it survive reboots
pm2 startup
pm2 save
```

Now your chatbot restarts automatically if it crashes or your computer reboots.

### Option B: Run on a Cheap VPS

Best for: reliability, serving customers 24/7.

Get a VPS from DigitalOcean or Hetzner ($5-10/month). SSH into it and run:

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull the model
ollama pull llama3.2

# Install Python dependencies
pip install fastapi uvicorn httpx slowapi

# Upload your chat_api.py file (use scp or paste it)
scp chat_api.py user@your-server-ip:~/

# Create a systemd service so it runs forever
sudo tee /etc/systemd/system/chatbot.service > /dev/null <<EOF
[Unit]
Description=AI Chatbot API
After=network.target

[Service]
User=$USER
WorkingDirectory=/home/$USER
ExecStart=/usr/bin/python3 /home/$USER/chat_api.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable chatbot
sudo systemctl start chatbot
```

Update `API_URL` in your widget to point to your VPS IP: `http://YOUR_SERVER_IP:9877`.

For production, put Cloudflare or nginx in front of it for HTTPS.

### Option C: Run on an Old Laptop

Got an old laptop collecting dust? Turn it into a dedicated AI server. Install Linux on it, follow the same steps as Option B, and point your widget at its local IP address.

For a complete guide on turning old hardware into a multi-machine AI system, check out the **AI Employee Guide ($19.99)** which covers the full infrastructure setup, SSH access, service management, and scaling to multiple machines.

---

## Chapter 8: Troubleshooting

### "Connection refused" when testing Ollama

Ollama is not running. Start it:

- **Mac**: Open the Ollama app from Applications
- **Linux**: Run `ollama serve` in a separate terminal
- **Windows**: Launch Ollama from Start Menu

### "Port already in use" when starting the server

Something else is using port 9877. Either kill it or use a different port:

```bash
# Find what is using the port
lsof -i :9877

# Or just use a different port
python -c "import uvicorn; uvicorn.run('chat_api:app', host='0.0.0.0', port=9878)"
```

Remember to update `API_URL` in the widget if you change the port.

### CORS errors in the browser console

Your website cannot reach the server. Check three things:

1. The server is running
2. `API_URL` in the widget matches your server address exactly
3. The CORS middleware in `chat_api.py` includes your website's domain

### Slow responses (10+ seconds)

The AI model is too large for your hardware. Switch to tinyllama:

```bash
ollama pull tinyllama
```

Then change `MODEL = "tinyllama"` in `chat_api.py` and restart the server.

### Widget does not appear on the page

Make sure the `<script>` tag is placed before `</body>`, not inside `<head>`. The widget needs the page body to exist before it can add itself.

---

## What Next?

You now have a working AI chatbot on your website. For free. Running on your own hardware.

If you want to go deeper and build a full multi-machine AI system with dedicated hardware, agent orchestration, and automation, check out the **AI Employee Guide** at behike.store.

---

*Built by Behike. More tools at behike.store.*
