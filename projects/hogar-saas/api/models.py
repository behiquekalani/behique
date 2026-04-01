"""
Hogar SaaS — Data Models

SQLite-backed models for residents, staff, tasks, medications, and compliance.
"""

import sqlite3
import os
import json
from datetime import datetime, date, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "hogar.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Create all tables."""
    conn = get_db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS hogares (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        address TEXT,
        phone TEXT,
        email TEXT,
        owner_name TEXT,
        license_number TEXT,
        license_expiry DATE,
        max_capacity INTEGER DEFAULT 20,
        current_residents INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS residents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hogar_id INTEGER NOT NULL,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        date_of_birth DATE,
        admission_date DATE DEFAULT CURRENT_DATE,
        room_number TEXT,
        emergency_contact_name TEXT,
        emergency_contact_phone TEXT,
        conditions TEXT,  -- JSON array of medical conditions
        allergies TEXT,   -- JSON array
        diet_restrictions TEXT,
        mobility_level TEXT DEFAULT 'independent',  -- independent, assisted, wheelchair, bedridden
        notes TEXT,
        active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS medications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resident_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        dosage TEXT NOT NULL,
        frequency TEXT NOT NULL,  -- daily, twice_daily, weekly, as_needed
        time_slots TEXT NOT NULL,  -- JSON array: ["08:00", "14:00", "20:00"]
        instructions TEXT,
        prescribing_doctor TEXT,
        pharmacy TEXT,
        refill_date DATE,
        active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (resident_id) REFERENCES residents(id)
    );

    CREATE TABLE IF NOT EXISTS staff (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hogar_id INTEGER NOT NULL,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        role TEXT NOT NULL,  -- nurse, aide, admin, cook, maintenance
        phone TEXT NOT NULL,  -- WhatsApp number
        whatsapp_id TEXT,
        shift TEXT DEFAULT 'day',  -- day, night, rotating
        certifications TEXT,  -- JSON array
        hire_date DATE DEFAULT CURRENT_DATE,
        active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hogar_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        category TEXT NOT NULL,  -- medication, hygiene, meals, activity, cleaning, inspection, admin
        priority TEXT DEFAULT 'normal',  -- low, normal, high, critical
        assigned_to INTEGER,  -- staff_id
        resident_id INTEGER,  -- if task is resident-specific
        scheduled_time TIME,
        scheduled_date DATE DEFAULT CURRENT_DATE,
        recurrence TEXT,  -- daily, weekday, weekly, monthly, once
        status TEXT DEFAULT 'pending',  -- pending, sent, acknowledged, completed, missed, overdue
        completed_at TIMESTAMP,
        completed_by INTEGER,  -- staff_id who completed
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (assigned_to) REFERENCES staff(id),
        FOREIGN KEY (resident_id) REFERENCES residents(id)
    );

    CREATE TABLE IF NOT EXISTS task_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id INTEGER NOT NULL,
        action TEXT NOT NULL,  -- created, sent, acknowledged, completed, missed, escalated
        performed_by INTEGER,  -- staff_id
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        notes TEXT,
        FOREIGN KEY (task_id) REFERENCES tasks(id)
    );

    CREATE TABLE IF NOT EXISTS compliance_requirements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,  -- health_dept, ases, fire, sanitation, staffing
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        frequency TEXT NOT NULL,  -- daily, weekly, monthly, quarterly, annual, once
        last_completed DATE,
        next_due DATE,
        responsible_role TEXT,  -- which staff role handles this
        documentation_required TEXT,  -- what paperwork is needed
        penalty_for_noncompliance TEXT,
        active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS compliance_checks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        requirement_id INTEGER NOT NULL,
        hogar_id INTEGER NOT NULL,
        status TEXT DEFAULT 'pending',  -- pending, compliant, non_compliant, in_progress
        checked_date DATE DEFAULT CURRENT_DATE,
        checked_by INTEGER,
        evidence TEXT,  -- file path or description
        notes TEXT,
        corrective_action TEXT,
        corrective_deadline DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (requirement_id) REFERENCES compliance_requirements(id)
    );

    CREATE TABLE IF NOT EXISTS daily_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hogar_id INTEGER NOT NULL,
        report_date DATE DEFAULT CURRENT_DATE,
        total_tasks INTEGER DEFAULT 0,
        completed_tasks INTEGER DEFAULT 0,
        missed_tasks INTEGER DEFAULT 0,
        medications_given INTEGER DEFAULT 0,
        medications_missed INTEGER DEFAULT 0,
        incidents TEXT,  -- JSON array of incident descriptions
        notes TEXT,
        generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hogar_id INTEGER NOT NULL,
        staff_id INTEGER,
        direction TEXT NOT NULL,  -- outgoing, incoming
        channel TEXT DEFAULT 'whatsapp',
        content TEXT NOT NULL,
        message_type TEXT DEFAULT 'task',  -- task, reminder, alert, report, response
        whatsapp_message_id TEXT,
        status TEXT DEFAULT 'queued',  -- queued, sent, delivered, read, failed
        sent_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
    conn.close()


# ── HELPER FUNCTIONS ──────────────────────────────────────────

def add_hogar(name, address=None, phone=None, email=None, owner_name=None, max_capacity=20):
    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO hogares (name, address, phone, email, owner_name, max_capacity) VALUES (?, ?, ?, ?, ?, ?)",
        (name, address, phone, email, owner_name, max_capacity)
    )
    hogar_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return hogar_id


def add_resident(hogar_id, first_name, last_name, date_of_birth=None, room_number=None,
                 conditions=None, allergies=None, mobility_level="independent"):
    conn = get_db()
    cursor = conn.execute(
        """INSERT INTO residents (hogar_id, first_name, last_name, date_of_birth, room_number,
           conditions, allergies, mobility_level) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (hogar_id, first_name, last_name, date_of_birth, room_number,
         json.dumps(conditions or []), json.dumps(allergies or []), mobility_level)
    )
    resident_id = cursor.lastrowid
    # Update resident count
    conn.execute("UPDATE hogares SET current_residents = current_residents + 1 WHERE id = ?", (hogar_id,))
    conn.commit()
    conn.close()
    return resident_id


def add_medication(resident_id, name, dosage, frequency, time_slots, instructions=None):
    conn = get_db()
    cursor = conn.execute(
        """INSERT INTO medications (resident_id, name, dosage, frequency, time_slots, instructions)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (resident_id, name, dosage, frequency, json.dumps(time_slots), instructions)
    )
    med_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return med_id


def add_staff(hogar_id, first_name, last_name, role, phone, shift="day"):
    conn = get_db()
    cursor = conn.execute(
        """INSERT INTO staff (hogar_id, first_name, last_name, role, phone, shift)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (hogar_id, first_name, last_name, role, phone, shift)
    )
    staff_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return staff_id


def create_task(hogar_id, title, category, description=None, priority="normal",
                assigned_to=None, resident_id=None, scheduled_time=None,
                scheduled_date=None, recurrence="once"):
    conn = get_db()
    cursor = conn.execute(
        """INSERT INTO tasks (hogar_id, title, description, category, priority, assigned_to,
           resident_id, scheduled_time, scheduled_date, recurrence)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (hogar_id, title, description, category, priority, assigned_to,
         resident_id, scheduled_time, scheduled_date or date.today().isoformat(), recurrence)
    )
    task_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return task_id


def complete_task(task_id, staff_id, notes=None):
    conn = get_db()
    conn.execute(
        "UPDATE tasks SET status = 'completed', completed_at = ?, completed_by = ?, notes = ? WHERE id = ?",
        (datetime.now().isoformat(), staff_id, notes, task_id)
    )
    conn.execute(
        "INSERT INTO task_logs (task_id, action, performed_by, notes) VALUES (?, 'completed', ?, ?)",
        (task_id, staff_id, notes)
    )
    conn.commit()
    conn.close()


def get_pending_tasks(hogar_id, date_str=None):
    conn = get_db()
    date_str = date_str or date.today().isoformat()
    tasks = conn.execute(
        """SELECT t.*, s.first_name || ' ' || s.last_name as staff_name,
           r.first_name || ' ' || r.last_name as resident_name
           FROM tasks t
           LEFT JOIN staff s ON t.assigned_to = s.id
           LEFT JOIN residents r ON t.resident_id = r.id
           WHERE t.hogar_id = ? AND t.scheduled_date = ? AND t.status IN ('pending', 'sent', 'overdue')
           ORDER BY t.scheduled_time, t.priority DESC""",
        (hogar_id, date_str)
    ).fetchall()
    conn.close()
    return [dict(t) for t in tasks]


def get_compliance_status(hogar_id):
    conn = get_db()
    checks = conn.execute(
        """SELECT cr.*, cc.status as check_status, cc.checked_date, cc.notes as check_notes
           FROM compliance_requirements cr
           LEFT JOIN compliance_checks cc ON cr.id = cc.requirement_id AND cc.hogar_id = ?
           WHERE cr.active = 1
           ORDER BY cr.category, cc.status""",
        (hogar_id,)
    ).fetchall()
    conn.close()
    return [dict(c) for c in checks]


def generate_daily_report(hogar_id, report_date=None):
    conn = get_db()
    report_date = report_date or date.today().isoformat()

    tasks = conn.execute(
        "SELECT * FROM tasks WHERE hogar_id = ? AND scheduled_date = ?",
        (hogar_id, report_date)
    ).fetchall()

    total = len(tasks)
    completed = len([t for t in tasks if t["status"] == "completed"])
    missed = len([t for t in tasks if t["status"] in ("missed", "overdue")])

    meds = conn.execute(
        """SELECT t.* FROM tasks t WHERE t.hogar_id = ? AND t.scheduled_date = ? AND t.category = 'medication'""",
        (hogar_id, report_date)
    ).fetchall()
    meds_given = len([m for m in meds if m["status"] == "completed"])
    meds_missed = len([m for m in meds if m["status"] in ("missed", "overdue")])

    conn.execute(
        """INSERT OR REPLACE INTO daily_reports (hogar_id, report_date, total_tasks, completed_tasks,
           missed_tasks, medications_given, medications_missed)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (hogar_id, report_date, total, completed, missed, meds_given, meds_missed)
    )
    conn.commit()
    conn.close()

    return {
        "date": report_date,
        "total_tasks": total,
        "completed": completed,
        "missed": missed,
        "completion_rate": f"{(completed/total*100):.0f}%" if total > 0 else "N/A",
        "medications_given": meds_given,
        "medications_missed": meds_missed,
    }


# Initialize DB on import
init_db()
