"""
Behike Unified Web Server
Serves storefront, BIOS dashboard, VR war room, and PR dashboard.
Works on both Mac (~/behique) and Windows (C:\behique).
"""

import os
import sys
import platform
import logging
import time
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# --- Path detection ---
if platform.system() == "Windows":
    BASE_DIR = Path(r"C:\behique")
    LOG_DIR = Path(r"C:\behique\logs")
else:
    BASE_DIR = Path.home() / "behique"
    LOG_DIR = BASE_DIR / "logs"

STOREFRONT_DIR = BASE_DIR / "storefront"
BIOS_DIR = BASE_DIR / "bios" / "dashboard"
PR_DIR = BASE_DIR / "bios" / "dashboard"  # PR dashboard lives alongside BIOS

LOG_DIR.mkdir(parents=True, exist_ok=True)

# --- Logging ---
log_file = LOG_DIR / "webserver.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("behike-webserver")

# --- App ---
app = FastAPI(title="Behike Web Server", docs_url=None, redoc_url=None)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

START_TIME = time.time()


# --- Access logging middleware ---
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    elapsed = time.time() - start
    logger.info(
        f"{request.client.host} {request.method} {request.url.path} "
        f"{response.status_code} {elapsed:.3f}s"
    )
    return response


# --- Health check ---
@app.get("/health")
async def health():
    uptime = time.time() - START_TIME
    return JSONResponse(
        {
            "status": "ok",
            "server": "behike-webserver",
            "uptime_seconds": round(uptime, 1),
            "timestamp": datetime.now().isoformat(),
            "platform": platform.system(),
            "storefront_available": STOREFRONT_DIR.is_dir(),
            "bios_available": BIOS_DIR.is_dir(),
        }
    )


# --- BIOS dashboard ---
@app.get("/bios/")
@app.get("/bios")
async def bios_index():
    index = BIOS_DIR / "index.html"
    if index.is_file():
        return FileResponse(index)
    return HTMLResponse("<h1>BIOS Dashboard</h1><p>index.html not found</p>", status_code=404)


@app.get("/bios/{path:path}")
async def bios_files(path: str):
    file_path = BIOS_DIR / path
    if file_path.is_file():
        return FileResponse(file_path)
    return HTMLResponse(f"Not found: /bios/{path}", status_code=404)


# --- VR War Room ---
@app.get("/vr/")
@app.get("/vr")
async def vr_index():
    warroom = BIOS_DIR / "warroom.html"
    if warroom.is_file():
        return FileResponse(warroom)
    return HTMLResponse("<h1>VR War Room</h1><p>warroom.html not found</p>", status_code=404)


@app.get("/vr/{path:path}")
async def vr_files(path: str):
    file_path = BIOS_DIR / path
    if file_path.is_file():
        return FileResponse(file_path)
    return HTMLResponse(f"Not found: /vr/{path}", status_code=404)


# --- PR Dashboard ---
@app.get("/pr/")
@app.get("/pr")
async def pr_index():
    # Look for polymarket or a dedicated PR dashboard
    pr_file = BIOS_DIR / "polymarket.html"
    if pr_file.is_file():
        return FileResponse(pr_file)
    # Fallback to hub
    hub_file = BIOS_DIR / "hub.html"
    if hub_file.is_file():
        return FileResponse(hub_file)
    return HTMLResponse("<h1>PR Dashboard</h1><p>No dashboard file found</p>", status_code=404)


@app.get("/pr/{path:path}")
async def pr_files(path: str):
    file_path = BIOS_DIR / path
    if file_path.is_file():
        return FileResponse(file_path)
    return HTMLResponse(f"Not found: /pr/{path}", status_code=404)


# --- Storefront ---
@app.get("/store/")
@app.get("/store")
async def store_index():
    index = STOREFRONT_DIR / "index.html"
    if index.is_file():
        return FileResponse(index)
    return HTMLResponse("<h1>Storefront</h1><p>index.html not found</p>", status_code=404)


@app.get("/store/{path:path}")
async def store_files(path: str):
    file_path = STOREFRONT_DIR / path
    if file_path.is_file():
        return FileResponse(file_path)
    return HTMLResponse(f"Not found: /store/{path}", status_code=404)


# --- Root: storefront ---
@app.get("/")
async def root():
    index = STOREFRONT_DIR / "index.html"
    if index.is_file():
        return FileResponse(index)
    return HTMLResponse(
        "<h1>Behike</h1>"
        "<ul>"
        '<li><a href="/store/">/store/</a> - Storefront</li>'
        '<li><a href="/bios/">/bios/</a> - BIOS Dashboard</li>'
        '<li><a href="/vr/">/vr/</a> - VR War Room</li>'
        '<li><a href="/pr/">/pr/</a> - PR Dashboard</li>'
        '<li><a href="/health">/health</a> - Health Check</li>'
        "</ul>"
    )


# --- Run ---
if __name__ == "__main__":
    port = 8080
    logger.info(f"Starting Behike Web Server on 0.0.0.0:{port}")
    logger.info(f"Platform: {platform.system()}")
    logger.info(f"Base dir: {BASE_DIR}")
    logger.info(f"Storefront: {STOREFRONT_DIR} (exists: {STOREFRONT_DIR.is_dir()})")
    logger.info(f"BIOS: {BIOS_DIR} (exists: {BIOS_DIR.is_dir()})")
    logger.info(f"Logs: {log_file}")

    uvicorn.run(
        "webserver:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info",
    )
