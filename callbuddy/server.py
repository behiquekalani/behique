"""
CallBuddy Backend Server
========================
FastAPI server that accepts call requests, queues them,
and serves the landing page static files.

Run: uvicorn server:app --port 8094 --reload
"""

import json
import uuid
import os
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI(title="CallBuddy API", version="1.0.0")

STORAGE_DIR = Path(__file__).parent / "storage"
REQUESTS_FILE = STORAGE_DIR / "requests.json"

# Ensure storage exists
STORAGE_DIR.mkdir(exist_ok=True)


# --- Models ---

class CallRequest(BaseModel):
    business_name: str
    phone_number: str
    purpose: str
    preferred_date: str = ""
    user_name: str = ""


class CallResponse(BaseModel):
    request_id: str
    status: str


# --- Storage helpers ---

def _load_requests() -> list[dict]:
    if not REQUESTS_FILE.exists():
        return []
    with open(REQUESTS_FILE, "r") as f:
        return json.load(f)


def _save_requests(requests: list[dict]):
    with open(REQUESTS_FILE, "w") as f:
        json.dump(requests, f, indent=2)


# --- API Routes ---

@app.post("/api/call", response_model=CallResponse)
async def create_call(req: CallRequest):
    """Queue a new call request."""
    request_id = str(uuid.uuid4())[:8]
    entry = {
        "request_id": request_id,
        "business_name": req.business_name,
        "phone_number": req.phone_number,
        "purpose": req.purpose,
        "preferred_date": req.preferred_date,
        "user_name": req.user_name,
        "status": "queued",
        "created_at": datetime.now().isoformat(),
    }

    requests = _load_requests()
    requests.append(entry)
    _save_requests(requests)

    return CallResponse(request_id=request_id, status="queued")


@app.get("/api/status/{request_id}")
async def get_status(request_id: str):
    """Get the status of a specific call request."""
    requests = _load_requests()
    for r in requests:
        if r["request_id"] == request_id:
            return r
    raise HTTPException(status_code=404, detail="Request not found")


@app.get("/api/calls")
async def list_calls():
    """List all call requests with their status."""
    requests = _load_requests()
    return {"calls": requests, "total": len(requests)}


# --- Static file serving for landing page ---
# Mount the callbuddy directory itself to serve index.html and assets.
# This must come after API routes so /api/* is matched first.

STATIC_DIR = Path(__file__).parent

# Serve index.html at root
@app.get("/")
async def serve_index():
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "CallBuddy API is running. No landing page found."}


# Mount static files for CSS/JS/images
app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8094)
