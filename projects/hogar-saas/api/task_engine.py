"""
Hogar SaaS — Task Engine

Generates daily tasks for a hogar based on:
- Resident medication schedules
- Routine care tasks (hygiene, meals, activities)
- Compliance requirements
- Custom recurring tasks

Runs every morning at 6 AM to generate the day's checklist.
"""

import json
from datetime import datetime, date, time, timedelta
from models import get_db, create_task, get_pending_tasks


class TaskEngine:
    """Generate daily tasks for a hogar."""

    # Standard daily tasks for any hogar
    ROUTINE_TASKS = [
        # Morning
        {"title": "Verificar signos vitales de todos los residentes", "time": "07:00", "category": "medication", "priority": "high"},
        {"title": "Preparar y servir desayuno", "time": "07:30", "category": "meals", "priority": "normal"},
        {"title": "Asistir con higiene personal (baño, vestimenta)", "time": "08:00", "category": "hygiene", "priority": "normal"},
        {"title": "Administrar medicamentos de la mañana", "time": "08:30", "category": "medication", "priority": "critical"},
        {"title": "Limpiar y desinfectar áreas comunes", "time": "09:00", "category": "cleaning", "priority": "normal"},
        {"title": "Actividad recreativa matutina", "time": "10:00", "category": "activity", "priority": "normal"},

        # Afternoon
        {"title": "Preparar y servir almuerzo", "time": "12:00", "category": "meals", "priority": "normal"},
        {"title": "Administrar medicamentos del mediodía", "time": "12:30", "category": "medication", "priority": "critical"},
        {"title": "Siesta / tiempo de descanso", "time": "13:00", "category": "activity", "priority": "low"},
        {"title": "Merienda de la tarde", "time": "15:00", "category": "meals", "priority": "normal"},
        {"title": "Actividad recreativa vespertina", "time": "16:00", "category": "activity", "priority": "normal"},

        # Evening
        {"title": "Preparar y servir cena", "time": "18:00", "category": "meals", "priority": "normal"},
        {"title": "Administrar medicamentos de la noche", "time": "19:00", "category": "medication", "priority": "critical"},
        {"title": "Asistir con rutina nocturna (higiene, ropa de dormir)", "time": "20:00", "category": "hygiene", "priority": "normal"},
        {"title": "Ronda nocturna de verificación", "time": "22:00", "category": "medication", "priority": "high"},
    ]

    # Weekly tasks
    WEEKLY_TASKS = {
        0: [  # Monday
            {"title": "Inventario de medicamentos", "time": "10:00", "category": "medication", "priority": "high"},
            {"title": "Revisión de expedientes de residentes", "time": "14:00", "category": "admin", "priority": "normal"},
        ],
        2: [  # Wednesday
            {"title": "Limpieza profunda de cocina", "time": "09:00", "category": "cleaning", "priority": "normal"},
            {"title": "Cambio de sábanas y ropa de cama", "time": "10:00", "category": "hygiene", "priority": "normal"},
        ],
        4: [  # Friday
            {"title": "Reporte semanal de actividades", "time": "15:00", "category": "admin", "priority": "normal"},
            {"title": "Verificar equipo de emergencia", "time": "16:00", "category": "inspection", "priority": "high"},
        ],
    }

    # Monthly tasks
    MONTHLY_TASKS = [
        {"title": "Simulacro de evacuación", "day": 1, "category": "inspection", "priority": "critical"},
        {"title": "Inspección de extintores", "day": 1, "category": "inspection", "priority": "high"},
        {"title": "Evaluación nutricional de residentes", "day": 15, "category": "medication", "priority": "normal"},
        {"title": "Reunión de personal", "day": 15, "category": "admin", "priority": "normal"},
        {"title": "Reporte mensual a Dept. de Salud", "day": 28, "category": "admin", "priority": "critical"},
    ]

    @classmethod
    def generate_daily_tasks(cls, hogar_id):
        """Generate all tasks for today."""
        today = date.today()
        weekday = today.weekday()
        day_of_month = today.day
        tasks_created = 0

        conn = get_db()

        # Get staff for assignment
        staff = conn.execute(
            "SELECT * FROM staff WHERE hogar_id = ? AND active = 1 ORDER BY role",
            (hogar_id,)
        ).fetchall()

        # Get residents for medication tasks
        residents = conn.execute(
            "SELECT * FROM residents WHERE hogar_id = ? AND active = 1",
            (hogar_id,)
        ).fetchall()

        conn.close()

        # Assign staff by role
        nurses = [s for s in staff if s["role"] in ("nurse", "aide")]
        cooks = [s for s in staff if s["role"] == "cook"]
        admins = [s for s in staff if s["role"] == "admin"]
        maintenance = [s for s in staff if s["role"] == "maintenance"]
        all_staff = list(staff)

        def pick_staff(category):
            if category in ("medication", "hygiene"):
                return nurses[0]["id"] if nurses else (all_staff[0]["id"] if all_staff else None)
            elif category == "meals":
                return cooks[0]["id"] if cooks else (all_staff[0]["id"] if all_staff else None)
            elif category in ("admin", "inspection"):
                return admins[0]["id"] if admins else (all_staff[0]["id"] if all_staff else None)
            elif category == "cleaning":
                return maintenance[0]["id"] if maintenance else (all_staff[0]["id"] if all_staff else None)
            return all_staff[0]["id"] if all_staff else None

        # Daily routine tasks
        for task in cls.ROUTINE_TASKS:
            task_id = create_task(
                hogar_id=hogar_id,
                title=task["title"],
                category=task["category"],
                priority=task["priority"],
                assigned_to=pick_staff(task["category"]),
                scheduled_time=task["time"],
                recurrence="daily"
            )
            tasks_created += 1

        # Per-resident medication tasks
        conn = get_db()
        for resident in residents:
            meds = conn.execute(
                "SELECT * FROM medications WHERE resident_id = ? AND active = 1",
                (resident["id"],)
            ).fetchall()

            for med in meds:
                time_slots = json.loads(med["time_slots"])
                for slot in time_slots:
                    task_id = create_task(
                        hogar_id=hogar_id,
                        title=f"Medicamento: {med['name']} {med['dosage']} → {resident['first_name']} {resident['last_name']}",
                        description=med["instructions"] or "",
                        category="medication",
                        priority="critical",
                        assigned_to=pick_staff("medication"),
                        resident_id=resident["id"],
                        scheduled_time=slot,
                        recurrence="daily"
                    )
                    tasks_created += 1
        conn.close()

        # Weekly tasks
        if weekday in cls.WEEKLY_TASKS:
            for task in cls.WEEKLY_TASKS[weekday]:
                create_task(
                    hogar_id=hogar_id,
                    title=task["title"],
                    category=task["category"],
                    priority=task["priority"],
                    assigned_to=pick_staff(task["category"]),
                    scheduled_time=task["time"],
                    recurrence="weekly"
                )
                tasks_created += 1

        # Monthly tasks
        for task in cls.MONTHLY_TASKS:
            if day_of_month == task["day"]:
                create_task(
                    hogar_id=hogar_id,
                    title=task["title"],
                    category=task["category"],
                    priority=task["priority"],
                    assigned_to=pick_staff(task["category"]),
                    recurrence="monthly"
                )
                tasks_created += 1

        return tasks_created

    @classmethod
    def get_overdue_tasks(cls, hogar_id):
        """Find tasks that should have been completed but weren't."""
        conn = get_db()
        now = datetime.now().strftime("%H:%M")
        today = date.today().isoformat()

        overdue = conn.execute(
            """SELECT t.*, s.first_name || ' ' || s.last_name as staff_name,
               s.phone as staff_phone
               FROM tasks t
               LEFT JOIN staff s ON t.assigned_to = s.id
               WHERE t.hogar_id = ? AND t.scheduled_date = ?
               AND t.status = 'pending' AND t.scheduled_time < ?
               AND t.priority IN ('high', 'critical')
               ORDER BY t.priority DESC, t.scheduled_time""",
            (hogar_id, today, now)
        ).fetchall()

        # Mark as overdue
        for task in overdue:
            conn.execute("UPDATE tasks SET status = 'overdue' WHERE id = ?", (task["id"],))

        conn.commit()
        conn.close()
        return [dict(t) for t in overdue]

    @classmethod
    def format_task_message(cls, tasks, staff_name=None):
        """Format tasks as a WhatsApp-friendly message."""
        if not tasks:
            return "✅ No hay tareas pendientes. ¡Buen trabajo!"

        header = f"📋 *Tareas para {staff_name or 'Hoy'}*\n"
        header += f"📅 {date.today().strftime('%A %d de %B, %Y')}\n"
        header += "─" * 30 + "\n\n"

        priority_emoji = {
            "critical": "🔴",
            "high": "🟡",
            "normal": "🟢",
            "low": "⚪",
        }

        msg = header
        current_category = ""

        for task in sorted(tasks, key=lambda t: (t.get("scheduled_time") or "99:99")):
            cat = task["category"]
            if cat != current_category:
                cat_names = {
                    "medication": "💊 MEDICAMENTOS",
                    "meals": "🍽️ COMIDAS",
                    "hygiene": "🚿 HIGIENE",
                    "activity": "🎮 ACTIVIDADES",
                    "cleaning": "🧹 LIMPIEZA",
                    "inspection": "📋 INSPECCIÓN",
                    "admin": "📁 ADMINISTRACIÓN",
                }
                msg += f"\n*{cat_names.get(cat, cat.upper())}*\n"
                current_category = cat

            emoji = priority_emoji.get(task["priority"], "⚪")
            time_str = task.get("scheduled_time") or ""
            resident = f" → {task.get('resident_name', '')}" if task.get("resident_name") else ""

            msg += f"{emoji} {time_str} {task['title']}{resident}\n"

        msg += f"\n─" * 30
        msg += f"\nTotal: {len(tasks)} tareas"
        msg += f"\nResponde '✅ [número]' para completar una tarea"

        return msg
