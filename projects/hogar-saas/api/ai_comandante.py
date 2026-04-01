"""
Hogar SaaS — AI Comandante

The general. Watches everything. Decides what needs attention.
Generates daily briefings, alerts, and strategic recommendations.
This is the white-collar brain of the hogar.
"""

import json
from datetime import datetime, date, timedelta
from models import get_db, generate_daily_report
from compliance_engine import ComplianceEngine
from scheduler import get_financial_summary


class AIComandante:
    """The AI that runs the hogar's operations."""

    def __init__(self, hogar_id):
        self.hogar_id = hogar_id
        self.compliance = ComplianceEngine(hogar_id)

    def morning_briefing(self):
        """Generate the daily morning briefing for the administrator."""
        conn = get_db()
        today = date.today()
        hogar = conn.execute("SELECT * FROM hogares WHERE id=?", (self.hogar_id,)).fetchone()

        # Today's tasks
        tasks = conn.execute(
            "SELECT COUNT(*) as total FROM tasks WHERE hogar_id=? AND scheduled_date=?",
            (self.hogar_id, today.isoformat())
        ).fetchone()

        # Critical tasks
        critical = conn.execute(
            "SELECT COUNT(*) as c FROM tasks WHERE hogar_id=? AND scheduled_date=? AND priority='critical'",
            (self.hogar_id, today.isoformat())
        ).fetchone()

        # Staff on shift today
        staff_today = conn.execute(
            "SELECT s.first_name, s.last_name, s.role, sh.start_time, sh.end_time FROM shifts sh JOIN staff s ON sh.staff_id=s.id WHERE sh.hogar_id=? AND sh.shift_date=?",
            (self.hogar_id, today.isoformat())
        ).fetchall()

        # Residents
        residents = conn.execute("SELECT COUNT(*) as c FROM residents WHERE hogar_id=? AND active=1", (self.hogar_id,)).fetchone()

        # Yesterday's report
        yesterday = (today - timedelta(days=1)).isoformat()
        yesterday_report = generate_daily_report(self.hogar_id, yesterday)

        # Compliance scan
        compliance = self.compliance.full_scan()

        # Upcoming deadlines
        upcoming = [i for i in compliance["issues"] if i["status"] == "at_risk"]

        # Financial snapshot
        financial = get_financial_summary(self.hogar_id)

        conn.close()

        briefing = f"""
Buenos dias. Aqui esta tu briefing del {today.strftime('%A %d de %B, %Y')}.

RESUMEN DEL HOGAR
  Residentes: {residents['c']}
  Tareas hoy: {tasks['total']} ({critical['c']} criticas)
  Personal programado: {len(staff_today)}
  Cumplimiento: {compliance['score']}% (Grado {compliance['grade']})

AYER
  Tareas completadas: {yesterday_report['completed']}/{yesterday_report['total_tasks']}
  Medicamentos: {yesterday_report['medications_given']} dados, {yesterday_report['medications_missed']} faltantes

"""
        if yesterday_report['medications_missed'] > 0:
            briefing += f"  ⚠️ ALERTA: {yesterday_report['medications_missed']} medicamentos no fueron administrados ayer.\n\n"

        if upcoming:
            briefing += "REQUIERE ATENCION\n"
            for item in upcoming[:5]:
                briefing += f"  ⚠️ {item['title']}: {item['details']}\n"
            briefing += "\n"

        if compliance['non_compliant'] > 0:
            briefing += f"CUMPLIMIENTO: {compliance['non_compliant']} requisitos NO cumplidos\n"
            for item in [i for i in compliance['issues'] if i['status'] == 'non_compliant'][:3]:
                briefing += f"  🔴 {item['title']}\n     → {item.get('corrective_action','')}\n"
            briefing += "\n"

        if staff_today:
            briefing += "PERSONAL HOY\n"
            for s in staff_today:
                briefing += f"  {s['first_name']} {s['last_name']} ({s['role']}) {s['start_time']}-{s['end_time']}\n"
            briefing += "\n"

        briefing += f"FINANZAS ({financial['month']})\n"
        briefing += f"  Ingresos: ${financial['total_revenue']:,.2f}\n"
        briefing += f"  Gastos: ${financial['total_expenses']:,.2f}\n"
        briefing += f"  Nomina: ${financial['payroll']:,.2f}\n"
        briefing += f"  Ganancia: ${financial['profit']:,.2f}\n"

        return briefing

    def detect_anomalies(self):
        """Detect unusual patterns that need attention."""
        conn = get_db()
        today = date.today()
        anomalies = []

        # Check for staff not clocking in
        scheduled = conn.execute(
            "SELECT sh.*, s.first_name, s.last_name FROM shifts sh JOIN staff s ON sh.staff_id=s.id WHERE sh.hogar_id=? AND sh.shift_date=? AND sh.status='scheduled' AND sh.start_time < ?",
            (self.hogar_id, today.isoformat(), datetime.now().strftime("%H:%M"))
        ).fetchall()
        for s in scheduled:
            anomalies.append({
                "type": "no_clock_in",
                "severity": "high",
                "message": f"{s['first_name']} {s['last_name']} no ha marcado entrada (turno: {s['start_time']})",
                "action": f"Contactar a {s['first_name']} inmediatamente"
            })

        # Check for overdue critical tasks
        overdue = conn.execute(
            "SELECT * FROM tasks WHERE hogar_id=? AND scheduled_date=? AND status='pending' AND priority='critical' AND scheduled_time < ?",
            (self.hogar_id, today.isoformat(), datetime.now().strftime("%H:%M"))
        ).fetchall()
        for t in overdue:
            anomalies.append({
                "type": "overdue_critical",
                "severity": "critical",
                "message": f"Tarea critica atrasada: {t['title']}",
                "action": "Completar inmediatamente. Esto afecta cumplimiento."
            })

        # Check medication adherence trend
        week_ago = (today - timedelta(days=7)).isoformat()
        med_stats = conn.execute(
            "SELECT scheduled_date, COUNT(*) as total, SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END) as done FROM tasks WHERE hogar_id=? AND category='medication' AND scheduled_date BETWEEN ? AND ? GROUP BY scheduled_date",
            (self.hogar_id, week_ago, today.isoformat())
        ).fetchall()

        if med_stats:
            rates = [s['done']/s['total']*100 if s['total']>0 else 0 for s in med_stats]
            avg_rate = sum(rates)/len(rates) if rates else 0
            if avg_rate < 90:
                anomalies.append({
                    "type": "low_med_adherence",
                    "severity": "critical",
                    "message": f"Adherencia a medicamentos esta semana: {avg_rate:.0f}% (objetivo: 100%)",
                    "action": "Revisar protocolo de medicamentos con el personal"
                })

        # Check expense anomalies
        this_month = today.strftime("%Y-%m")
        last_month = (today.replace(day=1) - timedelta(days=1)).strftime("%Y-%m")
        this_expenses = conn.execute("SELECT SUM(amount) as t FROM expenses WHERE hogar_id=? AND date LIKE ?", (self.hogar_id, f"{this_month}%")).fetchone()
        last_expenses = conn.execute("SELECT SUM(amount) as t FROM expenses WHERE hogar_id=? AND date LIKE ?", (self.hogar_id, f"{last_month}%")).fetchone()

        if this_expenses['t'] and last_expenses['t'] and this_expenses['t'] > last_expenses['t'] * 1.3:
            anomalies.append({
                "type": "expense_spike",
                "severity": "medium",
                "message": f"Gastos este mes (${this_expenses['t']:,.0f}) son 30%+ mas que el mes pasado (${last_expenses['t']:,.0f})",
                "action": "Revisar gastos recientes por categoría"
            })

        conn.close()
        return anomalies

    def weekly_strategy(self):
        """Generate weekly strategic recommendations."""
        compliance = self.compliance.full_scan()
        financial = get_financial_summary(self.hogar_id)
        anomalies = self.detect_anomalies()

        recommendations = []

        # Compliance recommendations
        if compliance['score'] < 80:
            recommendations.append("URGENTE: Cumplimiento por debajo del 80%. Enfocarse en requisitos criticos esta semana.")
        elif compliance['score'] < 95:
            recommendations.append(f"Cumplimiento en {compliance['score']}%. Objetivo: cerrar {compliance['non_compliant']} hallazgos pendientes.")

        # Financial recommendations
        if financial['profit'] < 0:
            recommendations.append(f"ALERTA: Operando con perdida de ${abs(financial['profit']):,.0f}. Revisar gastos y considerar ajuste de tarifas.")
        elif financial['profit'] < financial['total_revenue'] * 0.1:
            recommendations.append("Margen de ganancia menor al 10%. Buscar eficiencias en gastos operacionales.")

        # Staffing recommendations
        conn = get_db()
        overtime = conn.execute(
            "SELECT SUM(overtime_hours) as total_ot FROM shifts WHERE hogar_id=? AND shift_date >= ? AND overtime_hours > 0",
            (self.hogar_id, (date.today() - timedelta(days=7)).isoformat())
        ).fetchone()
        conn.close()

        if overtime['total_ot'] and overtime['total_ot'] > 20:
            recommendations.append(f"Horas extra esta semana: {overtime['total_ot']:.1f}h. Considerar contratar personal adicional.")

        # Anomaly-based recommendations
        critical_anomalies = [a for a in anomalies if a['severity'] == 'critical']
        if critical_anomalies:
            recommendations.append(f"{len(critical_anomalies)} anomalias criticas detectadas. Requieren atencion inmediata.")

        return {
            "week": date.today().isocalendar()[1],
            "compliance_score": compliance['score'],
            "compliance_grade": compliance['grade'],
            "financial_status": "profitable" if financial['profit'] > 0 else "loss",
            "profit": financial['profit'],
            "anomalies": len(anomalies),
            "critical_anomalies": len(critical_anomalies),
            "recommendations": recommendations,
        }
