#!/usr/bin/env python3
"""
Hogar SaaS Dashboard — Web interface for managing the hogar.
Serves a single-page dashboard showing tasks, residents, medications, compliance.

Usage:
    cd projects/hogar-saas
    python3 dashboard.py
    # Open http://localhost:8095
"""

import json
import os
import sys
from datetime import date, datetime
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

# Add api/ to path
sys.path.insert(0, str(Path(__file__).parent / "api"))
from models import get_db, get_pending_tasks, generate_daily_report, complete_task


class DashboardHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)

        if parsed.path == "/" or parsed.path == "/dashboard":
            self.serve_dashboard()
        elif parsed.path == "/api/tasks":
            self.serve_json(self.get_tasks())
        elif parsed.path == "/api/residents":
            self.serve_json(self.get_residents())
        elif parsed.path == "/api/report":
            self.serve_json(self.get_report())
        elif parsed.path == "/api/stats":
            self.serve_json(self.get_stats())
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path.startswith("/api/complete/"):
            task_id = int(self.path.split("/")[-1])
            complete_task(task_id, staff_id=1)
            self.serve_json({"status": "ok", "task_id": task_id})
        else:
            self.send_error(404)

    def serve_json(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

    def get_tasks(self):
        return get_pending_tasks(1)

    def get_residents(self):
        conn = get_db()
        residents = conn.execute("SELECT * FROM residents WHERE hogar_id = 1 AND active = 1").fetchall()
        result = []
        for r in residents:
            meds = conn.execute("SELECT * FROM medications WHERE resident_id = ? AND active = 1", (r["id"],)).fetchall()
            result.append({**dict(r), "medications": [dict(m) for m in meds]})
        conn.close()
        return result

    def get_report(self):
        return generate_daily_report(1)

    def get_stats(self):
        conn = get_db()
        total_tasks = conn.execute("SELECT COUNT(*) as c FROM tasks WHERE hogar_id = 1 AND scheduled_date = ?", (date.today().isoformat(),)).fetchone()["c"]
        completed = conn.execute("SELECT COUNT(*) as c FROM tasks WHERE hogar_id = 1 AND scheduled_date = ? AND status = 'completed'", (date.today().isoformat(),)).fetchone()["c"]
        residents = conn.execute("SELECT COUNT(*) as c FROM residents WHERE hogar_id = 1 AND active = 1").fetchone()["c"]
        staff = conn.execute("SELECT COUNT(*) as c FROM staff WHERE hogar_id = 1 AND active = 1").fetchone()["c"]
        conn.close()
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed,
            "completion_rate": f"{(completed/total_tasks*100):.0f}%" if total_tasks > 0 else "0%",
            "residents": residents,
            "staff": staff,
            "date": date.today().isoformat(),
        }

    def serve_dashboard(self):
        stats = self.get_stats()
        tasks = self.get_tasks()
        residents = self.get_residents()
        report = self.get_report()

        # Build task rows
        task_rows = ""
        for t in tasks:
            priority_colors = {"critical": "#ff4444", "high": "#ffd700", "normal": "#00c853", "low": "#888"}
            cat_emoji = {"medication": "💊", "meals": "🍽️", "hygiene": "🚿", "activity": "🎮", "cleaning": "🧹", "inspection": "📋", "admin": "📁"}
            p_color = priority_colors.get(t["priority"], "#888")
            emoji = cat_emoji.get(t["category"], "📝")

            resident_str = f' → {t["resident_name"]}' if t.get("resident_name") else ""
            task_rows += f"""
            <tr class="task-row" onclick="completeTask({t['id']})">
                <td><span style="color:{p_color}">●</span></td>
                <td>{t.get('scheduled_time','')}</td>
                <td>{emoji} {t['title']}{resident_str}</td>
                <td>{t['category']}</td>
                <td>{t.get('staff_name','Sin asignar')}</td>
                <td><span class="status-badge {t['status']}">{t['status']}</span></td>
            </tr>"""

        # Build resident cards
        resident_cards = ""
        for r in residents:
            conditions = json.loads(r.get("conditions", "[]"))
            med_count = len(r.get("medications", []))
            resident_cards += f"""
            <div class="resident-card">
                <div class="resident-name">{r['first_name']} {r['last_name']}</div>
                <div class="resident-meta">Hab. {r.get('room_number','-')} | {r['mobility_level']} | {med_count} medicamentos</div>
                <div class="resident-conditions">{', '.join(conditions) if conditions else 'Sin condiciones registradas'}</div>
            </div>"""

        html = f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Hogar Ana Gabriel — Dashboard</title>
<style>
:root{{--bg:#0a0a0a;--surface:#111;--card:#161616;--border:#222;--text:#e8e8e8;--dim:#777;--accent:#2d6a4f;--green:#00c853;--red:#ff4444;--gold:#ffd700}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,sans-serif;background:var(--bg);color:var(--text);min-height:100vh}}
.header{{background:var(--surface);border-bottom:1px solid var(--border);padding:16px 24px;display:flex;justify-content:space-between;align-items:center}}
.header h1{{font-size:18px;font-weight:800}}.header h1 span{{color:var(--accent)}}
.header-date{{font-size:13px;color:var(--dim)}}
.container{{max-width:1200px;margin:0 auto;padding:24px}}
.stats{{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin-bottom:24px}}
.stat{{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:16px;text-align:center}}
.stat-num{{font-size:28px;font-weight:900;margin-bottom:2px}}
.stat-label{{font-size:11px;color:var(--dim);text-transform:uppercase;letter-spacing:1px}}
.section{{margin-bottom:24px}}
.section-title{{font-size:14px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:var(--accent);margin-bottom:12px}}
table{{width:100%;border-collapse:collapse;background:var(--card);border-radius:12px;overflow:hidden;border:1px solid var(--border)}}
th{{background:var(--surface);padding:10px 12px;font-size:11px;text-transform:uppercase;letter-spacing:1px;color:var(--dim);text-align:left}}
td{{padding:10px 12px;border-bottom:1px solid var(--border);font-size:13px}}
.task-row{{cursor:pointer;transition:background .2s}}.task-row:hover{{background:var(--surface)}}
.status-badge{{padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600}}
.status-badge.pending{{background:rgba(255,215,0,.15);color:var(--gold)}}
.status-badge.completed{{background:rgba(0,200,83,.15);color:var(--green)}}
.status-badge.overdue{{background:rgba(255,68,68,.15);color:var(--red)}}
.resident-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:12px}}
.resident-card{{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:16px}}
.resident-name{{font-size:15px;font-weight:700;margin-bottom:4px}}
.resident-meta{{font-size:12px;color:var(--dim);margin-bottom:8px}}
.resident-conditions{{font-size:12px;color:var(--accent)}}
.whatsapp-btn{{position:fixed;bottom:24px;right:24px;background:#25d366;color:#fff;width:56px;height:56px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:28px;text-decoration:none;box-shadow:0 4px 16px rgba(37,211,102,.3)}}
@media(max-width:768px){{.stats{{grid-template-columns:repeat(2,1fr)}}.resident-grid{{grid-template-columns:1fr}}}}
</style></head><body>
<div class="header">
<h1>Hogar <span>Ana Gabriel</span></h1>
<div class="header-date">{date.today().strftime('%A %d de %B, %Y')}</div>
</div>
<div class="container">
<div class="stats">
<div class="stat"><div class="stat-num" style="color:var(--accent)">{stats['total_tasks']}</div><div class="stat-label">Tareas Hoy</div></div>
<div class="stat"><div class="stat-num" style="color:var(--green)">{stats['completed_tasks']}</div><div class="stat-label">Completadas</div></div>
<div class="stat"><div class="stat-num" style="color:{('#ff4444' if stats['total_tasks']-stats['completed_tasks']>0 else '#00c853')}">{stats['total_tasks']-stats['completed_tasks']}</div><div class="stat-label">Pendientes</div></div>
<div class="stat"><div class="stat-num" style="color:var(--accent)">{stats['residents']}</div><div class="stat-label">Residentes</div></div>
<div class="stat"><div class="stat-num" style="color:var(--accent)">{stats['staff']}</div><div class="stat-label">Personal</div></div>
</div>
<div class="section">
<div class="section-title">Tareas de Hoy (click para completar)</div>
<table><tr><th></th><th>Hora</th><th>Tarea</th><th>Categoría</th><th>Asignado</th><th>Estado</th></tr>
{task_rows}
</table></div>
<div class="section">
<div class="section-title">Residentes</div>
<div class="resident-grid">{resident_cards}</div>
</div>
</div>
<a href="https://wa.me/17875014445" class="whatsapp-btn" target="_blank">💬</a>
<script>
function completeTask(id){{
  fetch('/api/complete/'+id,{{method:'POST'}}).then(r=>r.json()).then(d=>{{
    if(d.status==='ok')location.reload();
  }});
}}
</script>
</body></html>"""

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode())

    def log_message(self, format, *args):
        pass  # Suppress request logs


def main():
    port = 8095
    server = HTTPServer(("0.0.0.0", port), DashboardHandler)
    print(f"\n  Hogar SaaS Dashboard running on http://localhost:{port}")
    print(f"  Phone access: http://$(ipconfig getifaddr en0):{port}")
    print(f"  Press Ctrl+C to stop\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Dashboard stopped.")


if __name__ == "__main__":
    main()
