"""
Behike API Gateway -- unified entry point for all services.
Port 8080 behind Cloudflare Tunnel on Naboria.
Replaces 8+ separate FastAPI servers with path-based routing.
"""
import json, logging, os, sys, time, hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# --- Paths ---
BASE_DIR = Path(os.getenv("BEHIKE_BASE", Path.home() / "behique"))
BIOS_DIR = BASE_DIR / "bios"
STOREFRONT_DIR = BASE_DIR / "storefront"
DASHBOARD_DIR = BIOS_DIR / "dashboard"
LOG_DIR = BIOS_DIR / "logs"
DATA_DIR = BIOS_DIR / "storage"
LOG_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# --- Logging ---
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_DIR / "gateway.log"), logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("gateway")

# --- App ---
app = FastAPI(title="Behike Gateway", docs_url=None, redoc_url=None)
START_TIME = time.time()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://behike.co", "https://www.behike.co",
                   "https://behike.store", "https://www.behike.store",
                   "http://localhost:8080"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

# --- Middleware: request logging ---
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    client = request.client.host if request.client else "unknown"
    log.info(f"{client} {request.method} {request.url.path} {response.status_code} {time.time()-start:.3f}s")
    return response

# --- Helpers ---
def _localhost_only(req: Request):
    if (req.client.host if req.client else "") not in ("127.0.0.1", "::1", "localhost"):
        raise HTTPException(403, "Localhost only")

def _json_path(name: str) -> Path: return DATA_DIR / f"{name}.json"
def _load(name: str): p = _json_path(name); return json.loads(p.read_text()) if p.is_file() else []
def _save(name: str, data): _json_path(name).write_text(json.dumps(data, indent=2, default=str))
def _now(): return datetime.now(timezone.utc).isoformat()
def _serve(directory: Path, path: str = "index.html"):
    f = directory / path
    return FileResponse(f) if f.is_file() else None

# ---- HEALTH ----
@app.get("/health")
async def health():
    return {"status": "ok", "server": "behike-gateway", "uptime_s": round(time.time() - START_TIME, 1),
            "ts": _now(), "storefront": STOREFRONT_DIR.is_dir(), "dashboard": DASHBOARD_DIR.is_dir()}

# ---- WEBHOOKS: /api/webhook/* ----
@app.post("/api/webhook/{provider}")
async def webhook_receive(provider: str, request: Request):
    ct = request.headers.get("content-type", "")
    body = await request.json() if ct.startswith("application/json") else {"raw": (await request.body()).decode()}
    events = _load("webhooks")
    events.append({"provider": provider, "ts": _now(), "payload": body})
    _save("webhooks", events[-500:])
    log.info(f"Webhook: {provider}")
    return {"ok": True}

@app.get("/api/webhook/log")
async def webhook_log(request: Request):
    _localhost_only(request); return _load("webhooks")

# ---- ANALYTICS: /api/analytics/* ----
@app.post("/api/analytics/event")
async def analytics_event(request: Request):
    data = await request.json()
    data.update(ts=_now(), ip=request.client.host if request.client else None,
                ua=request.headers.get("user-agent", ""))
    events = _load("analytics"); events.append(data)
    _save("analytics", events[-5000:])
    return {"ok": True}

@app.get("/api/analytics/summary")
async def analytics_summary(request: Request):
    _localhost_only(request)
    events = _load("analytics")
    pages: dict[str, int] = {}
    for e in events: pages[e.get("page", "?")] = pages.get(e.get("page", "?"), 0) + 1
    return {"total": len(events), "pages": pages}

# ---- A/B TESTING: /api/ab/* ----
@app.get("/api/ab/variant")
async def ab_variant(test: str = "default"):
    bucket = int(hashlib.md5(f"{test}{time.time()}".encode()).hexdigest(), 16) % 100
    return {"test": test, "variant": "A" if bucket < 50 else "B", "bucket": bucket}

@app.post("/api/ab/convert")
async def ab_convert(request: Request):
    data = await request.json(); data["ts"] = _now()
    c = _load("ab_conversions"); c.append(data); _save("ab_conversions", c[-2000:])
    return {"ok": True}

@app.get("/api/ab/results")
async def ab_results(request: Request):
    _localhost_only(request); return _load("ab_conversions")

# ---- AFFILIATE: /api/affiliate/* ----
@app.get("/api/affiliate/click")
async def affiliate_click(ref: str, url: str, request: Request):
    clicks = _load("affiliate_clicks")
    clicks.append({"ref": ref, "url": url, "ts": _now(), "ip": request.client.host if request.client else None})
    _save("affiliate_clicks", clicks[-5000:])
    return {"ok": True, "ref": ref}

@app.get("/api/affiliate/stats")
async def affiliate_stats(request: Request):
    _localhost_only(request)
    clicks = _load("affiliate_clicks")
    by_ref: dict[str, int] = {}
    for c in clicks: by_ref[c.get("ref", "?")] = by_ref.get(c.get("ref", "?"), 0) + 1
    return {"total": len(clicks), "by_ref": by_ref}

# ---- COUPONS: /api/coupon/* ----
@app.get("/api/coupon/validate")
async def coupon_validate(code: str):
    coupons = _load("coupons")
    if not isinstance(coupons, dict): coupons = {}
    c = coupons.get(code.upper())
    return {"valid": True, "code": code.upper(), **c} if c else {"valid": False, "code": code.upper()}

@app.post("/api/coupon/create")
async def coupon_create(request: Request):
    _localhost_only(request)
    data = await request.json()
    coupons = _load("coupons")
    if not isinstance(coupons, dict): coupons = {}
    code = data.get("code", "").upper()
    if not code: raise HTTPException(400, "code required")
    coupons[code] = {"discount": data.get("discount", 10), "type": data.get("type", "percent"),
                     "created": _now(), "active": True}
    _save("coupons", coupons)
    return {"ok": True, "code": code}

# ---- REVIEWS: /api/review/* ----
@app.post("/api/review/submit")
async def review_submit(request: Request):
    data = await request.json(); data.update(ts=_now(), approved=False)
    reviews = _load("reviews"); reviews.append(data); _save("reviews", reviews)
    return {"ok": True}

@app.get("/api/review/list")
async def review_list(product: Optional[str] = None, approved_only: bool = True):
    reviews = _load("reviews")
    if product: reviews = [r for r in reviews if r.get("product") == product]
    if approved_only: reviews = [r for r in reviews if r.get("approved")]
    return reviews

@app.post("/api/review/approve")
async def review_approve(request: Request):
    _localhost_only(request)
    idx = (await request.json()).get("index")
    reviews = _load("reviews")
    if idx is not None and 0 <= idx < len(reviews):
        reviews[idx]["approved"] = True; _save("reviews", reviews); return {"ok": True}
    raise HTTPException(400, "invalid index")

# ---- TRACK.JS: analytics pixel ----
TRACK_JS = """(function(){
  var ep=window.location.origin+"/api/analytics/event";
  function s(ev,x){var d={page:location.pathname,event:ev,ref:document.referrer};
    if(x)Object.assign(d,x);navigator.sendBeacon?navigator.sendBeacon(ep,JSON.stringify(d))
    :fetch(ep,{method:"POST",body:JSON.stringify(d),headers:{"Content-Type":"application/json"},keepalive:true});}
  s("pageview");document.addEventListener("click",function(e){
    var a=e.target.closest("a[href]");if(a)s("click",{target:a.href});});
})();"""

@app.get("/track.js")
async def track_js():
    return PlainTextResponse(TRACK_JS, media_type="application/javascript")

# ---- STATIC: storefront ----
@app.get("/")
async def root():
    for p in [STOREFRONT_DIR / "behike-co" / "index.html", STOREFRONT_DIR / "index.html"]:
        if p.is_file(): return FileResponse(p)
    return HTMLResponse("<h1>Behike</h1><p>Storefront not deployed yet.</p>")

@app.get("/links")
async def links_page():
    r = _serve(STOREFRONT_DIR, "links.html")
    if r: return r
    raise HTTPException(404, "links.html not found")

@app.get("/comparisons")
@app.get("/comparisons/")
async def comparisons_index():
    r = _serve(STOREFRONT_DIR / "comparisons")
    if r: return r
    raise HTTPException(404)

@app.get("/comparisons/{path:path}")
async def comparisons_files(path: str):
    r = _serve(STOREFRONT_DIR / "comparisons", path)
    if r: return r
    raise HTTPException(404)

@app.get("/store")
@app.get("/store/")
async def store_index():
    for p in [STOREFRONT_DIR / "behike-store" / "index.html", STOREFRONT_DIR / "index.html"]:
        if p.is_file(): return FileResponse(p)
    raise HTTPException(404, "Store not found")

@app.get("/store/{path:path}")
async def store_files(path: str):
    for base in [STOREFRONT_DIR / "behike-store", STOREFRONT_DIR]:
        if (base / path).is_file(): return FileResponse(base / path)
    raise HTTPException(404)

# ---- STATIC: dashboard (localhost only) ----
@app.get("/bios")
@app.get("/bios/")
async def bios_index(request: Request):
    _localhost_only(request)
    r = _serve(DASHBOARD_DIR)
    if r: return r
    raise HTTPException(404)

@app.get("/bios/{path:path}")
async def bios_files(path: str, request: Request):
    _localhost_only(request)
    r = _serve(DASHBOARD_DIR, path)
    if r: return r
    raise HTTPException(404)

# ---- Run ----
if __name__ == "__main__":
    port = int(os.getenv("GATEWAY_PORT", "8080"))
    log.info(f"Behike Gateway on 0.0.0.0:{port} | base={BASE_DIR}")
    uvicorn.run("gateway:app", host="0.0.0.0", port=port, reload=False, log_level="info")
