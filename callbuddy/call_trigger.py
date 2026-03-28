"""
CallBuddy - Vapi Call Trigger
=============================
Triggers outbound AI phone calls via the Vapi API.
Falls back to demo mode if VAPI_API_KEY is not set.

Vapi API key: sign up at https://vapi.ai and grab your key
from the dashboard under Settings > API Keys.

Set it as an environment variable:
  export VAPI_API_KEY="your-key-here"
"""

import json
import os
import time
import uuid
from datetime import datetime
from pathlib import Path

import requests

STORAGE_DIR = Path(__file__).parent / "storage"
CALL_LOGS_FILE = STORAGE_DIR / "call_logs.json"

# Ensure storage exists
STORAGE_DIR.mkdir(exist_ok=True)


class VapiCallTrigger:
    """Triggers and manages outbound calls through Vapi."""

    VAPI_BASE_URL = "https://api.vapi.ai"

    def __init__(self):
        # Load API key from environment. No hardcoded keys.
        self.api_key = os.environ.get("VAPI_API_KEY", "")
        self.demo_mode = not bool(self.api_key)

        if self.demo_mode:
            print("[CallBuddy] No VAPI_API_KEY found. Running in DEMO MODE.")
            print("[CallBuddy] Set VAPI_API_KEY env var to make real calls.")

    def _build_system_prompt(self, business_name: str, purpose: str, user_name: str) -> str:
        """Build the system prompt for the AI voice agent."""
        caller_name = user_name or "the user"
        return (
            f"You are an automated phone assistant calling on behalf of {caller_name}. "
            f"You are calling {business_name}. "
            f"Your purpose: {purpose}. "
            f"Be polite, professional, and concise. "
            f"If placed on hold, wait patiently and do not hang up. "
            f"If you hear hold music, remain on the line. "
            f"You are bilingual in English and Spanish. Respond in whichever language "
            f"the person on the other end uses. If unsure, start in English. "
            f"Identify yourself as an automated assistant calling on behalf of {caller_name}. "
            f"Collect any relevant information (confirmation numbers, dates, times, prices) "
            f"and summarize the call result clearly."
        )

    def _load_logs(self) -> list[dict]:
        if not CALL_LOGS_FILE.exists():
            return []
        with open(CALL_LOGS_FILE, "r") as f:
            return json.load(f)

    def _save_log(self, log_entry: dict):
        logs = self._load_logs()
        logs.append(log_entry)
        with open(CALL_LOGS_FILE, "w") as f:
            json.dump(logs, f, indent=2)

    def initiate_call(
        self,
        business_name: str,
        phone_number: str,
        purpose: str,
        user_name: str = "",
    ) -> dict:
        """
        Initiate an outbound call.

        In demo mode, simulates a successful call after 5 seconds.
        In live mode, uses the Vapi API to place a real call.

        Returns a dict with call_id, status, and result details.
        """
        call_id = str(uuid.uuid4())[:8]
        system_prompt = self._build_system_prompt(business_name, purpose, user_name)

        if self.demo_mode:
            return self._demo_call(call_id, business_name, phone_number, purpose, user_name, system_prompt)

        return self._live_call(call_id, business_name, phone_number, purpose, user_name, system_prompt)

    def _demo_call(
        self, call_id: str, business_name: str, phone_number: str,
        purpose: str, user_name: str, system_prompt: str
    ) -> dict:
        """Simulate a call for demo/testing purposes."""
        print(f"[DEMO] Simulating call to {business_name} at {phone_number}...")
        time.sleep(5)

        result = {
            "call_id": call_id,
            "mode": "demo",
            "business_name": business_name,
            "phone_number": phone_number,
            "purpose": purpose,
            "user_name": user_name,
            "status": "completed",
            "duration_seconds": 45,
            "summary": (
                f"[DEMO] Successfully called {business_name}. "
                f"The representative confirmed the request regarding: {purpose}. "
                f"No further action needed."
            ),
            "timestamp": datetime.now().isoformat(),
        }

        self._save_log(result)
        print(f"[DEMO] Call simulation complete. ID: {call_id}")
        return result

    def _live_call(
        self, call_id: str, business_name: str, phone_number: str,
        purpose: str, user_name: str, system_prompt: str
    ) -> dict:
        """Place a real call via the Vapi API."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "assistant": {
                "firstMessage": (
                    f"Hello, I'm an automated assistant calling on behalf of "
                    f"{user_name or 'a customer'}. I'm calling about: {purpose}."
                ),
                "model": {
                    "provider": "openai",
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": system_prompt}
                    ],
                },
                "voice": {
                    "provider": "11labs",
                    "voiceId": "21m00Tcm4TlvDq8ikWAM",  # Default voice
                },
            },
            "phoneNumberId": phone_number,
            "customer": {
                "number": phone_number,
            },
        }

        try:
            resp = requests.post(
                f"{self.VAPI_BASE_URL}/call/phone",
                headers=headers,
                json=payload,
                timeout=30,
            )
            resp.raise_for_status()
            vapi_data = resp.json()

            result = {
                "call_id": call_id,
                "vapi_call_id": vapi_data.get("id", ""),
                "mode": "live",
                "business_name": business_name,
                "phone_number": phone_number,
                "purpose": purpose,
                "user_name": user_name,
                "status": vapi_data.get("status", "initiated"),
                "summary": "Call initiated via Vapi. Check Vapi dashboard for real-time status.",
                "timestamp": datetime.now().isoformat(),
            }

        except requests.RequestException as e:
            result = {
                "call_id": call_id,
                "mode": "live",
                "business_name": business_name,
                "phone_number": phone_number,
                "purpose": purpose,
                "user_name": user_name,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

        self._save_log(result)
        return result


# Quick test when run directly
if __name__ == "__main__":
    trigger = VapiCallTrigger()
    result = trigger.initiate_call(
        business_name="Test Business",
        phone_number="+1234567890",
        purpose="Confirm appointment for tomorrow at 2pm",
        user_name="Kalani",
    )
    print(json.dumps(result, indent=2))
