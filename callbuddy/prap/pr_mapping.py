"""
PRAP PR Government Mapping
Puerto Rico Agentic Protocol - Maps intent actions to real PR government
agency data, including Spanish terms, required documents, IVR paths, and phone numbers.

This is the knowledge layer that lets an agent navigate PR bureaucracy.
"""

# ---------------------------------------------------------------------------
# PR_GOV_MAPPING
# Each key is an action intent. Values contain everything an agent needs
# to either call the agency (Shadow Protocol / CallBuddy) or route via MCP.
# ---------------------------------------------------------------------------
PR_GOV_MAPPING = {
    "renew_marbete": {
        "es_term": "Renovacion de marbete",
        "agency": "CESCO",
        "required_docs": [
            "titulo de propiedad del vehiculo",
            "seguro vigente (poliza)",
            "inspeccion mecanica aprobada",
            "identificacion con foto",
        ],
        # DTMF sequence to navigate the IVR phone tree
        "ivr_path": "1,3,1",
        "phone_number": "787-999-6200",
    },
    "property_tax": {
        "es_term": "Contribucion sobre propiedad (CRIM)",
        "agency": "CRIM",
        "required_docs": [
            "numero de cuenta CRIM",
            "escritura de propiedad o evidencia de titulo",
            "identificacion con foto",
        ],
        "ivr_path": "2,1",
        "phone_number": "787-722-2525",
    },
    "voter_id": {
        "es_term": "Tarjeta electoral",
        "agency": "CEE",
        "required_docs": [
            "certificado de nacimiento",
            "identificacion con foto vigente",
            "evidencia de residencia",
        ],
        "ivr_path": "1,1,2",
        "phone_number": "787-777-8682",
    },
    "pay_fine": {
        "es_term": "Pago de multas",
        "agency": "DTOP",
        "required_docs": [
            "numero de boleto o caso",
            "licencia de conducir",
            "identificacion con foto",
        ],
        "ivr_path": "3,2,1",
        "phone_number": "787-999-6200",
    },
    "schedule_appointment": {
        "es_term": "Cita en agencia gubernamental",
        "agency": "CESCO",
        "required_docs": [
            "identificacion con foto",
            "documentos relevantes al tramite",
        ],
        "ivr_path": "1,4",
        "phone_number": "787-999-6200",
    },
}


def translate_intent(action: str) -> dict:
    """
    Look up full agency mapping for a given action.

    Args:
        action: The intent action key (e.g. "renew_marbete").

    Returns:
        Dictionary with agency details, or None if action is unknown.
    """
    return PR_GOV_MAPPING.get(action)


def get_ivr_path(action: str) -> str:
    """
    Get just the DTMF sequence for navigating the agency's phone tree.

    Args:
        action: The intent action key.

    Returns:
        DTMF string (e.g. "1,3,1"), or None if action is unknown.
    """
    mapping = PR_GOV_MAPPING.get(action)
    if mapping:
        return mapping["ivr_path"]
    return None


# ---------------------------------------------------------------------------
# Quick test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("PRAP - PR Government Agency Mapping\n")
    for action, data in PR_GOV_MAPPING.items():
        print(f"  {action}:")
        print(f"    Agency: {data['agency']}")
        print(f"    Spanish: {data['es_term']}")
        print(f"    Phone: {data['phone_number']}")
        print(f"    IVR: {data['ivr_path']}")
        print(f"    Docs: {', '.join(data['required_docs'])}")
        print()
