#!/usr/bin/env python3
"""
Customer support ticket system. FastAPI standalone on port 8105.

Endpoints:
  POST /support/ticket       - submit a ticket
  GET  /support/tickets      - list tickets (filter: ?status=open)
  POST /support/reply/{id}   - admin reply to ticket
  POST /support/close/{id}   - close a ticket

Run: uvicorn bios.sales.support:app --port 8105
"""

import json, os, time, uuid
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional

# -- setup --
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
TICKETS_FILE = DATA_DIR / "tickets.json"

app = FastAPI(title="Behike Support", version="1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# -- auto-responses --
AUTO_REPLIES = [
    (["download"], "Check your email from Gumroad. Check spam folder."),
    (["refund"], "We offer 30-day refunds. Reply with your order number."),
    (["broken", "error"], "Try opening in a different browser. We'll help."),
]

# -- telegram (reuses notifier env vars) --
def _notify_telegram(ticket: dict):
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat = os.environ.get("TELEGRAM_CHAT_ID", "")
    if not token or not chat:
        print(f"[support] New ticket #{ticket['id'][:8]}: {ticket['subject']}")
        return
    import urllib.request
    msg = (
        f"<b>NEW SUPPORT TICKET</b>\n"
        f"ID: <code>{ticket['id'][:8]}</code>\n"
        f"From: {ticket['email']}\n"
        f"Subject: {ticket['subject']}\n"
        f"Product: {ticket.get('product', 'N/A')}"
    )
    payload = json.dumps({"chat_id": chat, "text": msg, "parse_mode": "HTML"}).encode()
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=payload, headers={"Content-Type": "application/json"}, method="POST",
    )
    try:
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        print(f"[support] Telegram error: {e}")

# -- storage --
def _load() -> list:
    if TICKETS_FILE.exists():
        return json.loads(TICKETS_FILE.read_text())
    return []

def _save(tickets: list):
    TICKETS_FILE.write_text(json.dumps(tickets, indent=2))

def _find(ticket_id: str, tickets: list):
    for t in tickets:
        if t["id"] == ticket_id or t["id"].startswith(ticket_id):
            return t
    return None

def _check_auto_reply(text: str) -> Optional[str]:
    lower = text.lower()
    for keywords, reply in AUTO_REPLIES:
        if any(k in lower for k in keywords):
            return reply
    return None

# -- models --
class TicketIn(BaseModel):
    email: str
    subject: str
    message: str
    product: Optional[str] = None

class ReplyIn(BaseModel):
    message: str

# -- routes --
@app.post("/support/ticket")
def create_ticket(t: TicketIn):
    tickets = _load()
    ticket = {
        "id": uuid.uuid4().hex[:12],
        "email": t.email,
        "subject": t.subject,
        "product": t.product,
        "status": "open",
        "created": time.strftime("%Y-%m-%d %H:%M:%S"),
        "thread": [{"from": "customer", "message": t.message, "time": time.strftime("%Y-%m-%d %H:%M:%S")}],
    }
    auto = _check_auto_reply(f"{t.subject} {t.message}")
    if auto:
        ticket["thread"].append({"from": "auto", "message": auto, "time": time.strftime("%Y-%m-%d %H:%M:%S")})
    tickets.append(ticket)
    _save(tickets)
    _notify_telegram(ticket)
    return {"ticket_id": ticket["id"], "auto_reply": auto}

@app.get("/support/tickets")
def list_tickets(status: Optional[str] = None):
    tickets = _load()
    if status:
        tickets = [t for t in tickets if t["status"] == status]
    return {"count": len(tickets), "tickets": tickets}

@app.post("/support/reply/{ticket_id}")
def reply_ticket(ticket_id: str, r: ReplyIn):
    tickets = _load()
    ticket = _find(ticket_id, tickets)
    if not ticket:
        raise HTTPException(404, "Ticket not found")
    ticket["thread"].append({"from": "admin", "message": r.message, "time": time.strftime("%Y-%m-%d %H:%M:%S")})
    ticket["status"] = "open"
    _save(tickets)
    return {"ok": True, "ticket_id": ticket["id"]}

@app.post("/support/close/{ticket_id}")
def close_ticket(ticket_id: str):
    tickets = _load()
    ticket = _find(ticket_id, tickets)
    if not ticket:
        raise HTTPException(404, "Ticket not found")
    ticket["status"] = "closed"
    _save(tickets)
    return {"ok": True, "ticket_id": ticket["id"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8105)
