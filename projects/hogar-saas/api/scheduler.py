"""
Hogar SaaS — Employee Scheduling System

Manages shifts, availability, time-off requests, and auto-scheduling.
"""

import json
from datetime import datetime, date, timedelta
from models import get_db


def init_scheduler_tables():
    conn = get_db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS shifts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hogar_id INTEGER NOT NULL,
        staff_id INTEGER NOT NULL,
        shift_date DATE NOT NULL,
        start_time TIME NOT NULL,
        end_time TIME NOT NULL,
        shift_type TEXT DEFAULT 'regular',
        status TEXT DEFAULT 'scheduled',
        clock_in TIME,
        clock_out TIME,
        hours_worked REAL DEFAULT 0,
        overtime_hours REAL DEFAULT 0,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (staff_id) REFERENCES staff(id)
    );

    CREATE TABLE IF NOT EXISTS time_off_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        staff_id INTEGER NOT NULL,
        request_date DATE NOT NULL,
        reason TEXT,
        status TEXT DEFAULT 'pending',
        approved_by INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS payroll (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hogar_id INTEGER NOT NULL,
        staff_id INTEGER NOT NULL,
        period_start DATE NOT NULL,
        period_end DATE NOT NULL,
        regular_hours REAL DEFAULT 0,
        overtime_hours REAL DEFAULT 0,
        hourly_rate REAL DEFAULT 10.50,
        overtime_rate REAL DEFAULT 15.75,
        gross_pay REAL DEFAULT 0,
        deductions REAL DEFAULT 0,
        net_pay REAL DEFAULT 0,
        status TEXT DEFAULT 'pending',
        paid_date DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hogar_id INTEGER NOT NULL,
        category TEXT NOT NULL,
        description TEXT NOT NULL,
        amount REAL NOT NULL,
        date DATE DEFAULT CURRENT_DATE,
        vendor TEXT,
        receipt_photo TEXT,
        approved_by INTEGER,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS revenue (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hogar_id INTEGER NOT NULL,
        resident_id INTEGER,
        category TEXT NOT NULL,
        description TEXT,
        amount REAL NOT NULL,
        date DATE DEFAULT CURRENT_DATE,
        source TEXT,
        status TEXT DEFAULT 'received',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
    conn.close()


def create_shift(hogar_id, staff_id, shift_date, start_time, end_time, shift_type="regular"):
    conn = get_db()
    conn.execute(
        "INSERT INTO shifts (hogar_id, staff_id, shift_date, start_time, end_time, shift_type) VALUES (?,?,?,?,?,?)",
        (hogar_id, staff_id, shift_date, start_time, end_time, shift_type)
    )
    conn.commit()
    conn.close()


def clock_in(shift_id):
    conn = get_db()
    now = datetime.now().strftime("%H:%M")
    conn.execute("UPDATE shifts SET clock_in=?, status='active' WHERE id=?", (now, shift_id))
    conn.commit()
    conn.close()


def clock_out(shift_id):
    conn = get_db()
    now = datetime.now().strftime("%H:%M")
    shift = conn.execute("SELECT * FROM shifts WHERE id=?", (shift_id,)).fetchone()
    if shift and shift["clock_in"]:
        ci = datetime.strptime(shift["clock_in"], "%H:%M")
        co = datetime.strptime(now, "%H:%M")
        hours = (co - ci).total_seconds() / 3600
        overtime = max(0, hours - 8)
        regular = min(hours, 8)
        conn.execute(
            "UPDATE shifts SET clock_out=?, status='completed', hours_worked=?, overtime_hours=? WHERE id=?",
            (now, hours, overtime, shift_id)
        )
    conn.commit()
    conn.close()


def auto_generate_weekly_schedule(hogar_id, week_start=None):
    """Auto-generate a week of shifts based on staff and needs."""
    conn = get_db()
    if not week_start:
        today = date.today()
        week_start = today - timedelta(days=today.weekday())

    staff = conn.execute("SELECT * FROM staff WHERE hogar_id=? AND active=1", (hogar_id,)).fetchall()
    conn.close()

    day_staff = [s for s in staff if s["shift"] in ("day", "rotating")]
    night_staff = [s for s in staff if s["shift"] in ("night", "rotating")]

    for day_offset in range(7):
        shift_date = (week_start + timedelta(days=day_offset)).isoformat()
        for i, s in enumerate(day_staff):
            if day_offset < 5 or i < len(day_staff) // 2:
                create_shift(hogar_id, s["id"], shift_date, "07:00", "15:00", "day")
        for s in night_staff:
            create_shift(hogar_id, s["id"], shift_date, "15:00", "23:00", "night")


def add_expense(hogar_id, category, description, amount, vendor=None, receipt=None):
    conn = get_db()
    conn.execute(
        "INSERT INTO expenses (hogar_id,category,description,amount,vendor,receipt_photo) VALUES (?,?,?,?,?,?)",
        (hogar_id, category, description, amount, vendor, receipt)
    )
    conn.commit()
    conn.close()


def add_revenue(hogar_id, category, amount, description=None, resident_id=None, source=None):
    conn = get_db()
    conn.execute(
        "INSERT INTO revenue (hogar_id,category,description,amount,resident_id,source) VALUES (?,?,?,?,?,?)",
        (hogar_id, category, description, amount, resident_id, source)
    )
    conn.commit()
    conn.close()


def calculate_payroll(hogar_id, period_start, period_end):
    """Calculate payroll for all staff in a period."""
    conn = get_db()
    staff = conn.execute("SELECT * FROM staff WHERE hogar_id=? AND active=1", (hogar_id,)).fetchall()
    payroll_records = []

    for s in staff:
        shifts = conn.execute(
            "SELECT * FROM shifts WHERE staff_id=? AND shift_date BETWEEN ? AND ? AND status='completed'",
            (s["id"], period_start, period_end)
        ).fetchall()

        regular = sum(min(sh["hours_worked"], 8) for sh in shifts)
        overtime = sum(sh["overtime_hours"] for sh in shifts)
        rate = 10.50
        ot_rate = rate * 1.5
        gross = (regular * rate) + (overtime * ot_rate)
        deductions = gross * 0.0765  # FICA
        net = gross - deductions

        conn.execute(
            """INSERT INTO payroll (hogar_id,staff_id,period_start,period_end,
               regular_hours,overtime_hours,hourly_rate,overtime_rate,gross_pay,deductions,net_pay)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (hogar_id, s["id"], period_start, period_end, regular, overtime, rate, ot_rate, gross, deductions, net)
        )
        payroll_records.append({"staff": f"{s['first_name']} {s['last_name']}", "regular": regular,
                                "overtime": overtime, "gross": gross, "net": net})

    conn.commit()
    conn.close()
    return payroll_records


def get_financial_summary(hogar_id, month=None):
    """Get monthly financial summary."""
    conn = get_db()
    if not month:
        month = date.today().strftime("%Y-%m")

    expenses = conn.execute(
        "SELECT category, SUM(amount) as total FROM expenses WHERE hogar_id=? AND date LIKE ? GROUP BY category",
        (hogar_id, f"{month}%")
    ).fetchall()

    revenue = conn.execute(
        "SELECT category, SUM(amount) as total FROM revenue WHERE hogar_id=? AND date LIKE ? GROUP BY category",
        (hogar_id, f"{month}%")
    ).fetchall()

    payroll = conn.execute(
        "SELECT SUM(gross_pay) as total_payroll FROM payroll WHERE hogar_id=? AND period_start LIKE ?",
        (hogar_id, f"{month}%")
    ).fetchone()

    total_expenses = sum(e["total"] for e in expenses) + (payroll["total_payroll"] or 0)
    total_revenue = sum(r["total"] for r in revenue)

    conn.close()
    return {
        "month": month,
        "revenue": {dict(r)["category"]: dict(r)["total"] for r in revenue},
        "expenses": {dict(e)["category"]: dict(e)["total"] for e in expenses},
        "payroll": payroll["total_payroll"] or 0,
        "total_revenue": total_revenue,
        "total_expenses": total_expenses,
        "profit": total_revenue - total_expenses,
    }


init_scheduler_tables()
