# CallBuddy - Full Product Spec (from Gemini)

## Market Gap
- 15M+ US adults with Social Anxiety Disorder
- No dedicated consumer app for making calls on behalf of anxious users
- Google Duplex limited to Google ecosystem
- Bland.ai/Vapi are B2B infrastructure, not consumer-facing

## Tech Stack (Vapi recommended for MVP)
- Vapi.ai: $0.05/min, ~500-800ms latency, best realism
- Bland.ai: $0.12/min, enterprise cold calls
- Retell AI: $0.10/min, developer friendly

## Business Model
- $14.99/mo subscription (20 calls cap)
- $1.99 per successful appointment (pay-per-success)
- PR market alone: 224K potential users, 1% capture = $22K/mo

## MVP Requirements
1. Web UI: business name, phone, purpose, date/time
2. Backend: FastAPI + Supabase
3. Voice: Vapi API with hold-music handling
4. Notification: SMS/push on completion
5. Landing page + waitlist for validation
6. Demo video of AI navigating real hold menu

## Legal
- Two-party consent for recording
- AI must identify as automated assistant
- HIPAA compliance needed for medical appointments (v2)

## PR-Specific Features
- Bilingual (Spanish/English)
- CESCO/Hacienda IVR navigation
- DTMF button pressing for phone menus
- Local slang awareness

## Marketing Channels
- Reddit: r/socialanxiety, r/adulting
- TikTok: "Things I didn't do because I was scared to call"

## Future: PRAP (Puerto Rico Agentic Protocol)
- Agent-to-Agent communication replacing voice calls
- OAuth 2.1 + JWT digital passports for AI agents
- MCP-based standardized government endpoints
- White paper ready for PRITS pitch
