"""
Hogar SaaS — WhatsApp Integration via Twilio

Sends task checklists, medication reminders, and alerts to staff.
Receives completion confirmations and voice notes.

Setup:
  1. Create Twilio account (twilio.com)
  2. Enable WhatsApp sandbox or business API
  3. Set env vars: TWILIO_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER
"""

import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

TWILIO_SID = os.environ.get("TWILIO_SID", "")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "")
TWILIO_WHATSAPP = os.environ.get("TWILIO_WHATSAPP_NUMBER", "")


class WhatsAppMessenger:
    """Send and receive WhatsApp messages via Twilio."""

    def __init__(self):
        self.client = None
        if TWILIO_SID and TWILIO_AUTH_TOKEN:
            try:
                from twilio.rest import Client
                self.client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
                logger.info("Twilio WhatsApp client initialized")
            except ImportError:
                logger.warning("twilio package not installed. Run: pip install twilio")
            except Exception as e:
                logger.error(f"Twilio init failed: {e}")

    def send_message(self, to_phone, message):
        """Send a WhatsApp message."""
        if not self.client:
            logger.info(f"[DRY RUN] WhatsApp to {to_phone}: {message[:100]}...")
            return {"status": "dry_run", "to": to_phone}

        try:
            # Format phone for WhatsApp
            to_whatsapp = f"whatsapp:+{to_phone.replace('+', '').replace('-', '').replace(' ', '')}"
            from_whatsapp = f"whatsapp:{TWILIO_WHATSAPP}"

            msg = self.client.messages.create(
                body=message,
                from_=from_whatsapp,
                to=to_whatsapp
            )

            logger.info(f"WhatsApp sent to {to_phone}: {msg.sid}")
            return {"status": "sent", "sid": msg.sid, "to": to_phone}

        except Exception as e:
            logger.error(f"WhatsApp send failed to {to_phone}: {e}")
            return {"status": "failed", "error": str(e), "to": to_phone}

    def send_task_checklist(self, staff_phone, staff_name, tasks):
        """Send formatted task checklist to a staff member."""
        from task_engine import TaskEngine
        message = TaskEngine.format_task_message(tasks, staff_name)
        return self.send_message(staff_phone, message)

    def send_medication_alert(self, staff_phone, resident_name, medication, dosage, time_slot):
        """Send urgent medication reminder."""
        message = (
            f"🔴 *MEDICAMENTO URGENTE*\n\n"
            f"Residente: *{resident_name}*\n"
            f"Medicamento: {medication}\n"
            f"Dosis: {dosage}\n"
            f"Hora programada: {time_slot}\n\n"
            f"Responde '✅' cuando esté administrado."
        )
        return self.send_message(staff_phone, message)

    def send_overdue_alert(self, staff_phone, overdue_tasks):
        """Send alert for overdue tasks."""
        task_list = "\n".join([f"⚠️ {t['title']} (programado: {t.get('scheduled_time', '?')})" for t in overdue_tasks[:5]])
        message = (
            f"⚠️ *TAREAS ATRASADAS*\n\n"
            f"{task_list}\n\n"
            f"Estas tareas están atrasadas. Complételas lo antes posible.\n"
            f"Responde '✅ [tarea]' para marcar como completada."
        )
        return self.send_message(staff_phone, message)

    def send_daily_report(self, admin_phone, report):
        """Send end-of-day report to admin."""
        message = (
            f"📊 *REPORTE DIARIO*\n"
            f"📅 {report['date']}\n\n"
            f"Total tareas: {report['total_tasks']}\n"
            f"Completadas: {report['completed']} ✅\n"
            f"Pendientes: {report['missed']} ❌\n"
            f"Cumplimiento: {report['completion_rate']}\n\n"
            f"💊 Medicamentos dados: {report['medications_given']}\n"
            f"💊 Medicamentos faltantes: {report['medications_missed']}\n\n"
        )

        if report['medications_missed'] > 0:
            message += "🔴 *ATENCIÓN: Hay medicamentos sin administrar.*\n"

        return self.send_message(admin_phone, message)

    def send_compliance_alert(self, admin_phone, requirement, days_until_due):
        """Send compliance deadline alert."""
        urgency = "🔴 URGENTE" if days_until_due <= 3 else "🟡 PRÓXIMO"
        message = (
            f"{urgency} *CUMPLIMIENTO*\n\n"
            f"Requisito: {requirement['title']}\n"
            f"Categoría: {requirement['category']}\n"
            f"Vence en: {days_until_due} días\n"
            f"Documentación requerida: {requirement.get('documentation_required', 'N/A')}\n\n"
            f"Acción requerida: Completar antes de la fecha límite."
        )
        return self.send_message(admin_phone, message)


def parse_incoming_message(message_body, from_phone):
    """Parse an incoming WhatsApp message from staff."""
    body = message_body.strip().lower()

    # Check for task completion
    if body.startswith("✅") or body.startswith("done") or body.startswith("listo"):
        # Extract task reference
        task_ref = body.replace("✅", "").replace("done", "").replace("listo", "").strip()
        return {"action": "complete_task", "reference": task_ref, "from": from_phone}

    # Check for help request
    if body in ("ayuda", "help", "?"):
        return {"action": "help", "from": from_phone}

    # Check for status request
    if body in ("status", "estado", "pendiente", "pendientes"):
        return {"action": "get_pending", "from": from_phone}

    # Check for emergency
    if any(w in body for w in ["emergencia", "emergency", "urgente", "caida", "fell"]):
        return {"action": "emergency", "message": message_body, "from": from_phone}

    # Default: log as note
    return {"action": "note", "message": message_body, "from": from_phone}
