"""
Hogar SaaS — Resident Health Trends

Track vitals over time. Detect trends before they become emergencies.
The system that caught Residente 4's blood pressure rising.
"""

import json
from datetime import datetime, date, timedelta
from models import get_db


def init_health_tables():
    conn = get_db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS vitals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resident_id INTEGER NOT NULL,
        recorded_by INTEGER,
        recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        blood_pressure_sys INTEGER,
        blood_pressure_dia INTEGER,
        heart_rate INTEGER,
        temperature REAL,
        oxygen_saturation INTEGER,
        weight REAL,
        blood_sugar INTEGER,
        notes TEXT,
        FOREIGN KEY (resident_id) REFERENCES residents(id)
    );

    CREATE TABLE IF NOT EXISTS incidents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hogar_id INTEGER NOT NULL,
        resident_id INTEGER,
        reported_by INTEGER,
        incident_type TEXT NOT NULL,
        severity TEXT DEFAULT 'medium',
        description TEXT NOT NULL,
        location TEXT,
        witnesses TEXT,
        action_taken TEXT,
        follow_up_required INTEGER DEFAULT 0,
        follow_up_notes TEXT,
        photo_evidence TEXT,
        reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        resolved_at TIMESTAMP,
        status TEXT DEFAULT 'open'
    );

    CREATE TABLE IF NOT EXISTS health_alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resident_id INTEGER NOT NULL,
        alert_type TEXT NOT NULL,
        metric TEXT NOT NULL,
        trend_direction TEXT,
        current_value REAL,
        baseline_value REAL,
        change_percent REAL,
        message TEXT NOT NULL,
        severity TEXT DEFAULT 'medium',
        acknowledged INTEGER DEFAULT 0,
        acknowledged_by INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
    conn.close()


def record_vitals(resident_id, staff_id, bp_sys=None, bp_dia=None, heart_rate=None,
                  temp=None, o2=None, weight=None, blood_sugar=None, notes=None):
    conn = get_db()
    conn.execute(
        """INSERT INTO vitals (resident_id, recorded_by, blood_pressure_sys, blood_pressure_dia,
           heart_rate, temperature, oxygen_saturation, weight, blood_sugar, notes)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (resident_id, staff_id, bp_sys, bp_dia, heart_rate, temp, o2, weight, blood_sugar, notes)
    )
    conn.commit()
    conn.close()

    # Check for alerts after recording
    check_trends(resident_id)


def report_incident(hogar_id, incident_type, description, resident_id=None,
                    reported_by=None, severity="medium", location=None, action_taken=None):
    conn = get_db()
    conn.execute(
        """INSERT INTO incidents (hogar_id, resident_id, reported_by, incident_type,
           severity, description, location, action_taken)
           VALUES (?,?,?,?,?,?,?,?)""",
        (hogar_id, resident_id, reported_by, incident_type, severity, description, location, action_taken)
    )
    conn.commit()
    conn.close()


def check_trends(resident_id):
    """Analyze vitals trends and generate alerts if concerning."""
    conn = get_db()
    alerts = []

    # Get last 10 readings
    readings = conn.execute(
        "SELECT * FROM vitals WHERE resident_id=? ORDER BY recorded_at DESC LIMIT 10",
        (resident_id,)
    ).fetchall()

    if len(readings) < 3:
        conn.close()
        return []

    readings = [dict(r) for r in readings]

    # Blood pressure trend
    bp_readings = [r["blood_pressure_sys"] for r in readings if r["blood_pressure_sys"]]
    if len(bp_readings) >= 3:
        recent_avg = sum(bp_readings[:3]) / 3
        older_avg = sum(bp_readings[3:min(6, len(bp_readings))]) / max(1, min(3, len(bp_readings)-3))
        if older_avg > 0:
            change = ((recent_avg - older_avg) / older_avg) * 100
            if change > 5:
                alert = create_alert(conn, resident_id, "blood_pressure_rising",
                    "blood_pressure_sys", "rising", recent_avg, older_avg, change,
                    f"Presion arterial subiendo: promedio {recent_avg:.0f} vs {older_avg:.0f} (cambio: {change:.1f}%)",
                    "high" if change > 10 else "medium")
                alerts.append(alert)
            elif change < -10:
                alert = create_alert(conn, resident_id, "blood_pressure_dropping",
                    "blood_pressure_sys", "dropping", recent_avg, older_avg, change,
                    f"Presion arterial bajando: promedio {recent_avg:.0f} vs {older_avg:.0f} (cambio: {change:.1f}%)",
                    "high")
                alerts.append(alert)

    # Heart rate trend
    hr_readings = [r["heart_rate"] for r in readings if r["heart_rate"]]
    if len(hr_readings) >= 3:
        latest = hr_readings[0]
        if latest > 100:
            alert = create_alert(conn, resident_id, "tachycardia",
                "heart_rate", "high", latest, 80, ((latest-80)/80)*100,
                f"Frecuencia cardiaca elevada: {latest} bpm",
                "high")
            alerts.append(alert)
        elif latest < 50:
            alert = create_alert(conn, resident_id, "bradycardia",
                "heart_rate", "low", latest, 70, ((latest-70)/70)*100,
                f"Frecuencia cardiaca baja: {latest} bpm",
                "critical")
            alerts.append(alert)

    # Weight trend (significant change)
    weight_readings = [r["weight"] for r in readings if r["weight"]]
    if len(weight_readings) >= 2:
        recent = weight_readings[0]
        previous = weight_readings[-1]
        if previous > 0:
            change = ((recent - previous) / previous) * 100
            if abs(change) > 5:
                direction = "aumento" if change > 0 else "perdida"
                alert = create_alert(conn, resident_id, f"weight_{direction}",
                    "weight", "rising" if change > 0 else "dropping", recent, previous, change,
                    f"Cambio significativo de peso: {direction} de {abs(change):.1f}% ({previous:.1f}→{recent:.1f} lbs)",
                    "medium")
                alerts.append(alert)

    # Oxygen saturation
    o2_readings = [r["oxygen_saturation"] for r in readings if r["oxygen_saturation"]]
    if o2_readings and o2_readings[0] < 92:
        alert = create_alert(conn, resident_id, "low_oxygen",
            "oxygen_saturation", "low", o2_readings[0], 95, ((o2_readings[0]-95)/95)*100,
            f"Saturacion de oxigeno baja: {o2_readings[0]}% (normal: >95%)",
            "critical")
        alerts.append(alert)

    # Blood sugar
    sugar_readings = [r["blood_sugar"] for r in readings if r["blood_sugar"]]
    if sugar_readings:
        latest = sugar_readings[0]
        if latest > 200:
            alert = create_alert(conn, resident_id, "high_blood_sugar",
                "blood_sugar", "high", latest, 120, ((latest-120)/120)*100,
                f"Azucar en sangre elevada: {latest} mg/dL",
                "high")
            alerts.append(alert)
        elif latest < 70:
            alert = create_alert(conn, resident_id, "low_blood_sugar",
                "blood_sugar", "low", latest, 100, ((latest-100)/100)*100,
                f"Azucar en sangre baja: {latest} mg/dL — HIPOGLUCEMIA",
                "critical")
            alerts.append(alert)

    conn.commit()
    conn.close()
    return alerts


def create_alert(conn, resident_id, alert_type, metric, direction, current, baseline, change, message, severity):
    conn.execute(
        """INSERT INTO health_alerts (resident_id, alert_type, metric, trend_direction,
           current_value, baseline_value, change_percent, message, severity)
           VALUES (?,?,?,?,?,?,?,?,?)""",
        (resident_id, alert_type, metric, direction, current, baseline, change, message, severity)
    )
    return {"type": alert_type, "message": message, "severity": severity}


def get_resident_health_summary(resident_id):
    """Get health overview for a resident."""
    conn = get_db()
    
    latest = conn.execute(
        "SELECT * FROM vitals WHERE resident_id=? ORDER BY recorded_at DESC LIMIT 1",
        (resident_id,)
    ).fetchone()

    alerts = conn.execute(
        "SELECT * FROM health_alerts WHERE resident_id=? AND acknowledged=0 ORDER BY created_at DESC",
        (resident_id,)
    ).fetchall()

    # Medication adherence (last 7 days)
    week_ago = (date.today() - timedelta(days=7)).isoformat()
    med_tasks = conn.execute(
        """SELECT COUNT(*) as total, 
           SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END) as done
           FROM tasks WHERE resident_id=? AND category='medication' AND scheduled_date>=?""",
        (resident_id, week_ago)
    ).fetchone()

    conn.close()

    adherence = (med_tasks['done']/med_tasks['total']*100) if med_tasks['total'] > 0 else 0

    return {
        "latest_vitals": dict(latest) if latest else None,
        "active_alerts": [dict(a) for a in alerts],
        "medication_adherence_7d": f"{adherence:.0f}%",
        "alert_count": len(alerts),
    }


init_health_tables()
