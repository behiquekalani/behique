# PRAP - Puerto Rico Agentic Protocol (Full Spec from Gemini)

## What This Is
A framework for AI agents to interact directly with PR government systems.
CallBuddy is the consumer product. PRAP is the infrastructure layer underneath.

## Architecture
1. Identity Layer: JWT passports, 5-min tokens, OAuth 2.1, DPoP
2. Communication Layer: MCP-based JSON requests
3. Shadow Protocol: Voice fallback when agency has no API
4. Bilingual Bridge: English user -> Spanish government

## Revenue Model
- Citizen: $0.50-$2 per transaction
- Government: SaaS fee for clean data intake
- PR market: 32K citizens at 1% adoption = $50-100K/year per agency

## MVP Components
- bios_identity_signer.py (JWT passport generator)
- bios_gateway.py (Flask API for A2A requests)
- prap_schema.json (standardized request format)
- callbuddy_vapi_trigger.py (voice fallback via Vapi)
- bios_translator.py (EN/ES mapping with PR terminology)

## PRAP JSON Schema
```json
{
  "protocol_version": "2026.1-beta",
  "transaction_id": "uuid-v4",
  "identity": {
    "passport_token": "JWT_STRING",
    "did": "did:bios:pr:user_123"
  },
  "intent": {
    "domain": "gov.pr.cesco",
    "action": "RENEW_MARBETE",
    "params": {
      "plate_number": "ABC-123",
      "vin_last_4": "9981"
    }
  },
  "constraints": {
    "max_fee_usd": 20.00,
    "deadline": "2026-04-01T23:59:59Z",
    "human_intervention_required": false
  }
}
```

## PR Government Mapping
- Marbete = Vehicle registration tag (CESCO)
- CRIM = Property tax (Centro de Recaudacion de Ingresos Municipales)
- Boletos = Fines/tickets
- Colecturia = Tax collection office
- Tarjeta Electoral = Voter ID

## IVR Navigation Paths
- CESCO appointments: Press 1 (Spanish), wait, Press 5 (Citas)
- CRIM certification: Press 2, wait, Press 1

## Agent State Machine
- DORMANT -> AUTHORIZED -> EXECUTING -> PENDING_APPROVAL -> COMPLETED
- REVOKED state via kill switch at any point

## Implementation Roadmap
- Phase 1: Sandbox with Colmena66 startups
- Phase 2: CESCO Marbete renewals via MCP
- Phase 3: Multi-agency A2A (top 10 PR agencies)
- Phase 4: Full citizen dashboard + monetization

## Pitch Angle for PRITS
"Puerto Rico can be the first US territory to align with NIST 2026 agentic identity standards."

## 60-Second Onboarding Script
"Your Marbete expires in 3 days. Instead of calling CESCO, you tell BIOS: fix my Marbete. BIOS generates a Digital Passport, navigates the Spanish IVR, stays on hold, books your appointment, and sends you a confirmation. You didn't dial a number."

## Tech Stack
- Vapi.ai for voice ($0.05/min)
- FastAPI + Supabase for backend
- ChromaDB for RAG knowledge base
- PyJWT for passport generation
- feedparser for RSS sources
