#!/usr/bin/env python3
"""
Seed compliance requirements — PR Dept de Salud, ASES, fire, sanitation, staffing rules.
Run once after seed_ana_gabriel.py to populate regulatory requirements.
"""

from datetime import date, timedelta
from models import get_db, init_db

init_db()


def seed_requirements():
    conn = get_db()

    requirements = [
        # ── DEPT DE SALUD ──
        {
            "category": "health_dept",
            "title": "Licencia de operación vigente",
            "description": "Licencia del Departamento de Salud para operar hogar de ancianos debe estar vigente y visible.",
            "frequency": "annual",
            "responsible_role": "admin",
            "documentation_required": "Licencia original, copia en expediente, exhibida en área visible",
            "penalty": "Cierre inmediato del hogar",
        },
        {
            "category": "health_dept",
            "title": "Expediente médico actualizado por residente",
            "description": "Cada residente debe tener expediente con historial médico, plan de cuidado, medicamentos, alergias y contacto de emergencia.",
            "frequency": "monthly",
            "responsible_role": "nurse",
            "documentation_required": "Expediente individual con firma del médico tratante",
            "penalty": "Multa y plan correctivo obligatorio",
        },
        {
            "category": "health_dept",
            "title": "Registro de administración de medicamentos",
            "description": "Registro diario firmado de cada medicamento administrado a cada residente, incluyendo hora, dosis y persona que administró.",
            "frequency": "daily",
            "responsible_role": "nurse",
            "documentation_required": "Hoja MAR (Medication Administration Record) firmada",
            "penalty": "Multa y posible suspensión de licencia",
        },
        {
            "category": "health_dept",
            "title": "Plan de cuidado individualizado",
            "description": "Plan de cuidado para cada residente revisado y actualizado, firmado por médico y enfermera.",
            "frequency": "quarterly",
            "responsible_role": "nurse",
            "documentation_required": "Plan de cuidado firmado por médico y enfermera encargada",
            "penalty": "Plan correctivo obligatorio",
        },
        {
            "category": "health_dept",
            "title": "Evaluación nutricional de residentes",
            "description": "Evaluación del estado nutricional de cada residente, menú aprobado por nutricionista.",
            "frequency": "monthly",
            "responsible_role": "admin",
            "documentation_required": "Informe nutricional, menú semanal firmado por nutricionista",
            "penalty": "Multa",
        },
        {
            "category": "health_dept",
            "title": "Control de signos vitales",
            "description": "Registro diario de signos vitales (presión, temperatura, pulso) de cada residente.",
            "frequency": "daily",
            "responsible_role": "nurse",
            "documentation_required": "Hoja de signos vitales firmada",
            "penalty": "Multa y plan correctivo",
        },
        {
            "category": "health_dept",
            "title": "Reporte de incidentes y caídas",
            "description": "Todo incidente, caída o cambio significativo en condición debe ser documentado dentro de 24 horas.",
            "frequency": "daily",
            "responsible_role": "nurse",
            "documentation_required": "Formulario de incidente completado y firmado",
            "penalty": "Multa significativa, posible investigación",
        },

        # ── ASES (ADMINISTRACIÓN DE SEGUROS DE SALUD) ──
        {
            "category": "ases",
            "title": "Certificación ASES vigente",
            "description": "Certificación de proveedor de ASES para recibir pagos del plan de salud del gobierno.",
            "frequency": "annual",
            "responsible_role": "admin",
            "documentation_required": "Certificado ASES, contrato vigente",
            "penalty": "Pérdida de pagos del gobierno",
        },
        {
            "category": "ases",
            "title": "Facturación mensual a ASES",
            "description": "Envío de facturación correcta a ASES por servicios prestados a residentes cubiertos.",
            "frequency": "monthly",
            "responsible_role": "admin",
            "documentation_required": "Factura, evidencia de servicios, documentación de residentes",
            "penalty": "Rechazo de factura, pérdida de ingresos",
        },

        # ── SEGURIDAD Y FUEGO ──
        {
            "category": "fire",
            "title": "Inspección de extintores",
            "description": "Todos los extintores deben estar cargados, accesibles y con inspección mensual documentada.",
            "frequency": "monthly",
            "responsible_role": "maintenance",
            "documentation_required": "Tag de inspección en cada extintor, registro firmado",
            "penalty": "Multa del Cuerpo de Bomberos",
        },
        {
            "category": "fire",
            "title": "Simulacro de evacuación",
            "description": "Simulacro de evacuación con todo el personal y residentes. Documentar tiempo, participantes, observaciones.",
            "frequency": "quarterly",
            "responsible_role": "admin",
            "documentation_required": "Reporte de simulacro con fotos, lista de participantes, tiempo",
            "penalty": "Multa y orden de corrección",
        },
        {
            "category": "fire",
            "title": "Plan de evacuación actualizado",
            "description": "Plan de evacuación visible en cada área, con rutas marcadas y punto de encuentro designado.",
            "frequency": "annual",
            "responsible_role": "admin",
            "documentation_required": "Plan impreso exhibido, copia en expediente",
            "penalty": "Orden de corrección inmediata",
        },
        {
            "category": "fire",
            "title": "Detectores de humo y alarmas funcionales",
            "description": "Verificar funcionamiento de todos los detectores de humo, alarmas de incendio y luces de emergencia.",
            "frequency": "monthly",
            "responsible_role": "maintenance",
            "documentation_required": "Registro de prueba mensual firmado",
            "penalty": "Cierre parcial hasta corrección",
        },

        # ── SANIDAD ──
        {
            "category": "sanitation",
            "title": "Inspección sanitaria de cocina",
            "description": "Cocina debe cumplir con requisitos sanitarios: temperatura de alimentos, almacenamiento, limpieza, control de plagas.",
            "frequency": "monthly",
            "responsible_role": "cook",
            "documentation_required": "Registro de temperaturas, limpieza, control de plagas",
            "penalty": "Multa y posible cierre de cocina",
        },
        {
            "category": "sanitation",
            "title": "Certificado de salud del personal de cocina",
            "description": "Todo personal que manipula alimentos debe tener certificado de salud vigente.",
            "frequency": "annual",
            "responsible_role": "cook",
            "documentation_required": "Certificado de salud individual vigente",
            "penalty": "Multa, personal no puede cocinar",
        },
        {
            "category": "sanitation",
            "title": "Limpieza y desinfección de áreas comunes",
            "description": "Protocolo documentado de limpieza diaria de áreas comunes, baños y habitaciones.",
            "frequency": "daily",
            "responsible_role": "maintenance",
            "documentation_required": "Registro de limpieza firmado por turno",
            "penalty": "Orden de corrección",
        },
        {
            "category": "sanitation",
            "title": "Control de plagas",
            "description": "Servicio de fumigación por compañía certificada. Sin evidencia de plagas.",
            "frequency": "monthly",
            "responsible_role": "admin",
            "documentation_required": "Factura de fumigación, certificado de compañía",
            "penalty": "Multa y orden de fumigación inmediata",
        },

        # ── PERSONAL / STAFFING ──
        {
            "category": "staffing",
            "title": "Ratio personal-residente adecuado",
            "description": "Mínimo 1 enfermera por cada 15 residentes en turno de día, 1 por cada 20 en noche. Siempre al menos 2 personal presente.",
            "frequency": "daily",
            "responsible_role": "admin",
            "documentation_required": "Registro de asistencia del personal por turno",
            "penalty": "Multa y posible suspensión",
        },
        {
            "category": "staffing",
            "title": "Certificaciones del personal vigentes",
            "description": "Todo personal de enfermería debe tener licencia vigente de la Junta Examinadora. CPR certification para todo staff.",
            "frequency": "annual",
            "responsible_role": "admin",
            "documentation_required": "Copias de licencias y certificaciones en expediente de personal",
            "penalty": "Personal no puede trabajar sin certificación vigente",
        },
        {
            "category": "staffing",
            "title": "Capacitación continua del personal",
            "description": "Mínimo 12 horas de educación continua por año por empleado. Temas: cuidado de ancianos, emergencias, derechos del residente.",
            "frequency": "quarterly",
            "responsible_role": "admin",
            "documentation_required": "Certificados de asistencia, registro de horas de capacitación",
            "penalty": "Plan correctivo, posible multa",
        },
        {
            "category": "staffing",
            "title": "Expediente de personal completo",
            "description": "Cada empleado debe tener expediente con: contrato, certificaciones, certificado de salud, antecedentes penales, evaluaciones.",
            "frequency": "annual",
            "responsible_role": "admin",
            "documentation_required": "Expediente completo por empleado",
            "penalty": "Multa por expediente incompleto",
        },
    ]

    # Calculate due dates based on frequency
    freq_days = {
        "daily": 1,
        "weekly": 7,
        "monthly": 30,
        "quarterly": 90,
        "annual": 365,
    }

    for req in requirements:
        days = freq_days.get(req["frequency"], 30)
        next_due = (date.today() + timedelta(days=days)).isoformat()

        conn.execute(
            """INSERT INTO compliance_requirements
               (category, title, description, frequency, next_due, responsible_role,
                documentation_required, penalty_for_noncompliance)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (req["category"], req["title"], req["description"], req["frequency"],
             next_due, req["responsible_role"], req["documentation_required"], req["penalty"])
        )

    conn.commit()
    print(f"Seeded {len(requirements)} compliance requirements")

    # Create initial compliance checks for hogar 1 (Ana Gabriel)
    reqs = conn.execute("SELECT id, frequency FROM compliance_requirements WHERE active = 1").fetchall()
    for r in reqs:
        conn.execute(
            "INSERT INTO compliance_checks (requirement_id, hogar_id, status) VALUES (?, 1, 'pending')",
            (r["id"],)
        )
    conn.commit()
    print(f"Created {len(reqs)} initial compliance checks for Hogar Ana Gabriel")
    conn.close()


if __name__ == "__main__":
    seed_requirements()
