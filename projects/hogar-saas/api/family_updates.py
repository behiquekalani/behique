"""
Family Updates — Send activity photos to families via WhatsApp.

NOT medical data. NOT health records. Just: "Your loved one had a good day."
Photos of activities, meals, social events. Peace of mind, not HIPAA.

The daycare model: parents get photos of their kids. Families get photos of their elders.
"""

import json
from datetime import datetime, date
from models import get_db


def init_family_tables():
    conn = get_db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS family_contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resident_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        relationship TEXT NOT NULL,
        phone TEXT NOT NULL,
        email TEXT,
        receives_updates INTEGER DEFAULT 1,
        update_frequency TEXT DEFAULT 'daily',
        preferred_channel TEXT DEFAULT 'whatsapp',
        consent_given INTEGER DEFAULT 0,
        consent_date DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (resident_id) REFERENCES residents(id)
    );

    CREATE TABLE IF NOT EXISTS activity_updates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hogar_id INTEGER NOT NULL,
        resident_id INTEGER,
        update_type TEXT DEFAULT 'activity',
        description TEXT NOT NULL,
        photo_path TEXT,
        shared_with TEXT,
        sent_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
    conn.close()


def add_family_contact(resident_id, name, relationship, phone, consent=True):
    conn = get_db()
    conn.execute(
        """INSERT INTO family_contacts 
           (resident_id, name, relationship, phone, consent_given, consent_date) 
           VALUES (?, ?, ?, ?, ?, ?)""",
        (resident_id, name, relationship, phone, 1 if consent else 0, 
         date.today().isoformat() if consent else None)
    )
    conn.commit()
    conn.close()


def capture_activity_update(hogar_id, description, photo_path=None, resident_id=None):
    """Staff captures a moment — photo + short description."""
    conn = get_db()
    conn.execute(
        "INSERT INTO activity_updates (hogar_id, resident_id, description, photo_path) VALUES (?,?,?,?)",
        (hogar_id, resident_id, description, photo_path)
    )
    conn.commit()
    conn.close()


def get_todays_updates(hogar_id):
    conn = get_db()
    updates = conn.execute(
        """SELECT au.*, r.first_name, r.last_name 
           FROM activity_updates au 
           LEFT JOIN residents r ON au.resident_id = r.id 
           WHERE au.hogar_id = ? AND DATE(au.created_at) = ? 
           ORDER BY au.created_at DESC""",
        (hogar_id, date.today().isoformat())
    ).fetchall()
    conn.close()
    return [dict(u) for u in updates]


def send_family_updates(hogar_id):
    """Send today's activity updates to family contacts."""
    conn = get_db()
    updates = get_todays_updates(hogar_id)
    
    if not updates:
        return {"sent": 0, "message": "No hay actualizaciones hoy"}

    # Group updates by resident
    by_resident = {}
    general = []
    for u in updates:
        if u.get("resident_id"):
            by_resident.setdefault(u["resident_id"], []).append(u)
        else:
            general.append(u)

    sent_count = 0

    # Send resident-specific updates to their families
    for resident_id, resident_updates in by_resident.items():
        contacts = conn.execute(
            "SELECT * FROM family_contacts WHERE resident_id=? AND receives_updates=1 AND consent_given=1",
            (resident_id,)
        ).fetchall()

        for contact in contacts:
            message = format_family_message(contact, resident_updates, general)
            # In production: send via WhatsApp (whatsapp.py)
            # For now: log it
            conn.execute(
                "INSERT INTO messages (hogar_id, staff_id, direction, content, message_type) VALUES (?,NULL,'outgoing',?,?)",
                (hogar_id, message, "family_update")
            )
            sent_count += 1

    conn.commit()
    conn.close()
    return {"sent": sent_count, "updates": len(updates)}


def format_family_message(contact, resident_updates, general_updates):
    """Format a WhatsApp message for a family member."""
    contact = dict(contact)
    resident_name = None
    
    msg = f"Hola {contact['name']} 👋\n\n"
    msg += f"Aqui esta la actualizacion de hoy de Hogar Ana Gabriel:\n\n"

    for u in resident_updates:
        name = f"{u.get('first_name','')} {u.get('last_name','')}"
        if not resident_name:
            resident_name = name
        msg += f"📸 {u['description']}\n"
        if u.get('photo_path'):
            msg += f"[Foto adjunta]\n"
        msg += "\n"

    if general_updates:
        msg += "Actividades del hogar hoy:\n"
        for u in general_updates:
            msg += f"🏠 {u['description']}\n"
        msg += "\n"

    msg += f"Con carino,\nHogar Ana Gabriel 💚\n"
    msg += f"(787) 501-4445"

    return msg


init_family_tables()
