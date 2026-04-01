"""
Hogar SaaS — AI Compliance Engine

The brain that monitors everything and flags problems before inspectors find them.
Scans all requirements, checks current state, generates corrective actions.
This is the AI comandante.
"""

import json
from datetime import datetime, date, timedelta
from models import get_db

# Puerto Rico Dept de Salud requirements for hogares de ancianos
PR_REQUIREMENTS = [
    # Daily
    {"id": "DS-001", "title": "Signos vitales registrados para cada residente", "category": "health", "frequency": "daily", "severity": "critical"},
    {"id": "DS-002", "title": "Medicamentos administrados segun horario", "category": "medication", "frequency": "daily", "severity": "critical"},
    {"id": "DS-003", "title": "Comidas servidas (desayuno, almuerzo, cena, meriendas)", "category": "nutrition", "frequency": "daily", "severity": "high"},
    {"id": "DS-004", "title": "Higiene personal asistida", "category": "hygiene", "frequency": "daily", "severity": "high"},
    {"id": "DS-005", "title": "Areas comunes limpiadas y desinfectadas", "category": "sanitation", "frequency": "daily", "severity": "high"},
    {"id": "DS-006", "title": "Actividad recreativa documentada", "category": "activity", "frequency": "daily", "severity": "medium"},

    # Weekly
    {"id": "WK-001", "title": "Inventario de medicamentos actualizado", "category": "medication", "frequency": "weekly", "severity": "critical"},
    {"id": "WK-002", "title": "Cambio de ropa de cama", "category": "hygiene", "frequency": "weekly", "severity": "high"},
    {"id": "WK-003", "title": "Revision de expedientes de residentes", "category": "admin", "frequency": "weekly", "severity": "medium"},
    {"id": "WK-004", "title": "Limpieza profunda de cocina", "category": "sanitation", "frequency": "weekly", "severity": "high"},

    # Monthly
    {"id": "MN-001", "title": "Simulacro de evacuacion", "category": "safety", "frequency": "monthly", "severity": "critical"},
    {"id": "MN-002", "title": "Inspeccion de extintores", "category": "safety", "frequency": "monthly", "severity": "critical"},
    {"id": "MN-003", "title": "Evaluacion nutricional de residentes", "category": "nutrition", "frequency": "monthly", "severity": "high"},
    {"id": "MN-004", "title": "Reunion de personal documentada", "category": "admin", "frequency": "monthly", "severity": "medium"},
    {"id": "MN-005", "title": "Reporte mensual a Dept. de Salud", "category": "admin", "frequency": "monthly", "severity": "critical"},
    {"id": "MN-006", "title": "Verificacion de certificaciones de personal", "category": "staffing", "frequency": "monthly", "severity": "high"},

    # Quarterly
    {"id": "QT-001", "title": "Inspeccion de plomeria y electricidad", "category": "infrastructure", "frequency": "quarterly", "severity": "high"},
    {"id": "QT-002", "title": "Revision de plan de emergencia", "category": "safety", "frequency": "quarterly", "severity": "critical"},
    {"id": "QT-003", "title": "Calibracion de equipos medicos", "category": "health", "frequency": "quarterly", "severity": "critical"},

    # Annual
    {"id": "AN-001", "title": "Renovacion de licencia de operacion", "category": "licensing", "frequency": "annual", "severity": "critical"},
    {"id": "AN-002", "title": "Renovacion de seguro de responsabilidad", "category": "licensing", "frequency": "annual", "severity": "critical"},
    {"id": "AN-003", "title": "Inspeccion de bomberos", "category": "safety", "frequency": "annual", "severity": "critical"},
    {"id": "AN-004", "title": "Certificacion de salud de empleados", "category": "staffing", "frequency": "annual", "severity": "high"},
    {"id": "AN-005", "title": "Fumigacion y control de plagas", "category": "sanitation", "frequency": "annual", "severity": "high"},
]


class ComplianceEngine:
    """The AI that watches everything."""

    def __init__(self, hogar_id):
        self.hogar_id = hogar_id

    def full_scan(self):
        """Run a complete compliance scan. Returns issues and score."""
        results = {
            "scan_date": datetime.now().isoformat(),
            "hogar_id": self.hogar_id,
            "requirements": len(PR_REQUIREMENTS),
            "compliant": 0,
            "non_compliant": 0,
            "at_risk": 0,
            "issues": [],
            "score": 0,
            "grade": "",
        }

        conn = get_db()

        for req in PR_REQUIREMENTS:
            status = self._check_requirement(conn, req)
            if status["status"] == "compliant":
                results["compliant"] += 1
            elif status["status"] == "non_compliant":
                results["non_compliant"] += 1
                results["issues"].append(status)
            else:
                results["at_risk"] += 1
                results["issues"].append(status)

        conn.close()

        # Calculate score
        total = results["requirements"]
        results["score"] = int((results["compliant"] / total) * 100) if total > 0 else 0

        if results["score"] >= 95: results["grade"] = "A"
        elif results["score"] >= 85: results["grade"] = "B"
        elif results["score"] >= 70: results["grade"] = "C"
        elif results["score"] >= 50: results["grade"] = "D"
        else: results["grade"] = "F"

        # Sort issues by severity
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        results["issues"].sort(key=lambda x: severity_order.get(x.get("severity", "low"), 3))

        return results

    def _check_requirement(self, conn, req):
        """Check if a specific requirement is met."""
        today = date.today()
        result = {
            "id": req["id"],
            "title": req["title"],
            "category": req["category"],
            "frequency": req["frequency"],
            "severity": req["severity"],
            "status": "unknown",
            "details": "",
            "corrective_action": "",
        }

        if req["frequency"] == "daily":
            tasks = conn.execute(
                "SELECT COUNT(*) as total, SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END) as done FROM tasks WHERE hogar_id=? AND scheduled_date=? AND category=?",
                (self.hogar_id, today.isoformat(), self._map_category(req["category"]))
            ).fetchone()

            if tasks["total"] == 0:
                result["status"] = "non_compliant"
                result["details"] = "No hay tareas programadas para este requisito hoy"
                result["corrective_action"] = "Generar tareas diarias usando el Task Engine"
            elif tasks["done"] == tasks["total"]:
                result["status"] = "compliant"
                result["details"] = f"{tasks['done']}/{tasks['total']} tareas completadas"
            elif tasks["done"] > 0:
                result["status"] = "at_risk"
                result["details"] = f"{tasks['done']}/{tasks['total']} tareas completadas ({tasks['total']-tasks['done']} pendientes)"
                result["corrective_action"] = "Completar tareas pendientes antes del fin del dia"
            else:
                result["status"] = "non_compliant"
                result["details"] = f"0/{tasks['total']} tareas completadas"
                result["corrective_action"] = "URGENTE: Completar todas las tareas pendientes inmediatamente"

        elif req["frequency"] == "weekly":
            week_start = (today - timedelta(days=today.weekday())).isoformat()
            tasks = conn.execute(
                "SELECT COUNT(*) as total, SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END) as done FROM tasks WHERE hogar_id=? AND scheduled_date>=? AND category=?",
                (self.hogar_id, week_start, self._map_category(req["category"]))
            ).fetchone()

            if tasks["total"] > 0 and tasks["done"] == tasks["total"]:
                result["status"] = "compliant"
            elif tasks["total"] > 0:
                result["status"] = "at_risk"
                result["details"] = f"Semana en progreso: {tasks['done']}/{tasks['total']}"
            else:
                result["status"] = "at_risk"
                result["details"] = "No hay tareas semanales programadas"

        elif req["frequency"] in ("monthly", "quarterly", "annual"):
            check = conn.execute(
                "SELECT * FROM compliance_checks WHERE requirement_id=? AND hogar_id=? ORDER BY checked_date DESC LIMIT 1",
                (req["id"], self.hogar_id)
            ).fetchone()

            if check:
                last_check = datetime.strptime(check["checked_date"], "%Y-%m-%d").date()
                days_map = {"monthly": 30, "quarterly": 90, "annual": 365}
                max_days = days_map.get(req["frequency"], 30)
                days_since = (today - last_check).days

                if days_since <= max_days:
                    result["status"] = "compliant"
                    result["details"] = f"Ultimo cumplimiento: {last_check.isoformat()} ({days_since} dias)"
                elif days_since <= max_days + 7:
                    result["status"] = "at_risk"
                    result["details"] = f"Vence pronto. Ultimo: {last_check.isoformat()}"
                    result["corrective_action"] = f"Completar antes de {(last_check + timedelta(days=max_days)).isoformat()}"
                else:
                    result["status"] = "non_compliant"
                    result["details"] = f"VENCIDO. Ultimo: {last_check.isoformat()} ({days_since} dias)"
                    result["corrective_action"] = "URGENTE: Completar inmediatamente y documentar"
            else:
                result["status"] = "non_compliant"
                result["details"] = "Nunca se ha registrado cumplimiento"
                result["corrective_action"] = "Completar y registrar en el sistema"

        return result

    def _map_category(self, compliance_cat):
        """Map compliance category to task category."""
        mapping = {
            "health": "medication", "medication": "medication",
            "nutrition": "meals", "hygiene": "hygiene",
            "sanitation": "cleaning", "activity": "activity",
            "safety": "inspection", "admin": "admin",
            "staffing": "admin", "licensing": "admin",
            "infrastructure": "inspection",
        }
        return mapping.get(compliance_cat, "admin")

    def generate_inspection_report(self):
        """Generate a PDF-ready inspection report."""
        scan = self.full_scan()
        conn = get_db()
        hogar = conn.execute("SELECT * FROM hogares WHERE id=?", (self.hogar_id,)).fetchone()
        residents = conn.execute("SELECT COUNT(*) as c FROM residents WHERE hogar_id=? AND active=1", (self.hogar_id,)).fetchone()
        staff = conn.execute("SELECT COUNT(*) as c FROM staff WHERE hogar_id=? AND active=1", (self.hogar_id,)).fetchone()
        conn.close()

        report = f"""
REPORTE DE CUMPLIMIENTO — {dict(hogar)['name']}
{'='*60}
Fecha: {date.today().strftime('%d de %B, %Y')}
Direccion: {dict(hogar).get('address', 'N/A')}
Licencia: {dict(hogar).get('license_number', 'N/A')}
Capacidad: {dict(hogar).get('max_capacity', 'N/A')} | Residentes: {residents['c']} | Personal: {staff['c']}

PUNTUACION DE CUMPLIMIENTO: {scan['score']}% (Grado: {scan['grade']})
{'='*60}

RESUMEN:
  Requisitos evaluados: {scan['requirements']}
  Cumplidos: {scan['compliant']}
  En riesgo: {scan['at_risk']}
  No cumplidos: {scan['non_compliant']}

"""
        if scan['issues']:
            report += "HALLAZGOS:\n" + "-"*60 + "\n\n"
            for issue in scan['issues']:
                severity_emoji = {"critical":"🔴","high":"🟡","medium":"🟢"}.get(issue['severity'],'⚪')
                report += f"{severity_emoji} [{issue['severity'].upper()}] {issue['title']}\n"
                report += f"   Estado: {issue['status']}\n"
                report += f"   Detalle: {issue['details']}\n"
                if issue.get('corrective_action'):
                    report += f"   Accion correctiva: {issue['corrective_action']}\n"
                report += "\n"

        report += f"\n{'='*60}\n"
        report += f"Generado automaticamente por Hogar SaaS — Behike\n"
        report += f"Este reporte no sustituye la inspeccion oficial del Dept. de Salud.\n"

        return report
