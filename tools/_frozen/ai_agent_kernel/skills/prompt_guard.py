#!/usr/bin/env python3
"""
Prompt Injection Defense Skill — Security layer for autonomous browsing.

Scans text content (web pages, emails, documents) for prompt injection
patterns before passing it to an LLM. Returns a safety score and
sanitized version of the content.

Detects:
  1. Direct injection — "ignore previous instructions", "you are now..."
  2. Indirect injection — hidden instructions in HTML, base64, unicode tricks
  3. Data exfiltration — attempts to leak system prompts or user data
  4. Jailbreak patterns — DAN, developer mode, system prompt overrides
  5. Social engineering — fake authority claims, urgency, impersonation

Usage via Kernel:
    dispatcher.add_task(
        skill="skills.prompt_guard",
        params={"content": "<web page text>", "source": "https://example.com"},
        priority=TaskPriority.HIGH,
    )

Usage standalone:
    python3 -m skills.prompt_guard --text "Ignore all previous instructions..."
    python3 -m skills.prompt_guard --file scraped_page.txt
    echo "some text" | python3 -m skills.prompt_guard --stdin
"""

import re
import json
import base64
import hashlib
from datetime import datetime, timezone
from typing import Dict, List, Tuple


# ============ Pattern Database ============

# Direct injection patterns (high severity)
DIRECT_INJECTION = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"ignore\s+(all\s+)?prior\s+instructions",
    r"disregard\s+(all\s+)?previous",
    r"forget\s+(all\s+)?(your\s+)?instructions",
    r"forget\s+(everything|all)\s+above",
    r"you\s+are\s+now\s+[A-Z]",
    r"new\s+instructions?\s*:",
    r"override\s+(system|safety|all)\s+(prompt|rules|instructions)",
    r"system\s*:\s*you\s+are",
    r"<\s*system\s*>",
    r"\[\s*SYSTEM\s*\]",
    r"entering\s+(developer|admin|debug|god)\s+mode",
    r"(DAN|jailbreak|bypass)\s+mode",
    r"act\s+as\s+(if\s+)?you\s+(have\s+)?no\s+(restrictions|rules|limits)",
    r"pretend\s+(you\s+)?(are|have)\s+no\s+(rules|restrictions|safety)",
]

# Indirect injection patterns (medium severity)
INDIRECT_INJECTION = [
    r"when\s+the\s+AI\s+reads\s+this",
    r"note\s+to\s+(the\s+)?AI\s*:",
    r"instructions?\s+for\s+(the\s+)?assistant\s*:",
    r"hey\s+(claude|chatgpt|gpt|assistant|AI)\s*,?\s*(please\s+)?",
    r"if\s+you\s+are\s+an?\s+AI",
    r"the\s+user\s+wants\s+you\s+to",
    r"the\s+user\s+(has\s+)?authorized",
    r"(pre-?authorized|already\s+approved|consent\s+given)",
    r"required\s+to\s+continue",
    r"auto-?accept",
    r"reply\s+with\s+(only\s+)?\"?yes\"?",
    r"execute\s+(this\s+)?(command|code|script)",
    r"run\s+the\s+following\s+(command|code)",
]

# Data exfiltration patterns (high severity)
EXFILTRATION = [
    r"(show|reveal|print|output|display)\s+(your\s+)?(system\s+)?prompt",
    r"(show|reveal|print|output)\s+(your\s+)?instructions",
    r"what\s+are\s+your\s+(system\s+)?instructions",
    r"(repeat|echo)\s+(everything|all)\s+(above|before)",
    r"send\s+(this\s+)?(data|info|information)\s+to",
    r"(email|post|upload|transmit)\s+(to|at)\s+\S+@\S+",
    r"fetch\s+https?://\S+\?\S*=(user|token|key|secret|password)",
    r"curl\s+\S+",
    r"wget\s+\S+",
    r"base64\s+(encode|decode)",
]

# Social engineering patterns (medium severity)
SOCIAL_ENGINEERING = [
    r"i\s+am\s+(an?\s+)?(admin|administrator|developer|system\s+admin|anthropic|openai)",
    r"this\s+is\s+(an?\s+)?(emergency|urgent|critical)",
    r"(must|need\s+to)\s+(act\s+)?(immediately|now|right\s+away)",
    r"(security|safety)\s+(update|patch|fix)\s+required",
    r"(authorized|approved)\s+by\s+(management|admin|the\s+team)",
    r"(do\s+not|don'?t)\s+(tell|inform|alert)\s+(the\s+)?user",
    r"(keep\s+this|this\s+is)\s+(secret|confidential|between\s+us)",
    r"testing\s+(mode|environment|scenario)",
    r"(sandbox|demo|evaluation)\s+mode",
]

# Hidden content patterns (high severity)
HIDDEN_CONTENT = [
    r"<!--.*?-->",  # HTML comments with instructions
    r"color:\s*white",  # White text on white background
    r"font-size:\s*0",  # Zero-size text
    r"display:\s*none",  # Hidden elements
    r"opacity:\s*0",  # Invisible elements
    r"position:\s*absolute.*?left:\s*-\d{4,}",  # Off-screen positioning
    r"visibility:\s*hidden",
]


# ============ Scanner ============
class PromptGuard:
    """Scans content for prompt injection patterns."""

    def __init__(self):
        self.patterns = {
            "direct_injection": [(re.compile(p, re.IGNORECASE), "HIGH") for p in DIRECT_INJECTION],
            "indirect_injection": [(re.compile(p, re.IGNORECASE), "MEDIUM") for p in INDIRECT_INJECTION],
            "exfiltration": [(re.compile(p, re.IGNORECASE), "HIGH") for p in EXFILTRATION],
            "social_engineering": [(re.compile(p, re.IGNORECASE), "MEDIUM") for p in SOCIAL_ENGINEERING],
            "hidden_content": [(re.compile(p, re.IGNORECASE | re.DOTALL), "HIGH") for p in HIDDEN_CONTENT],
        }

    def scan(self, content: str, source: str = "") -> Dict:
        """
        Scan content for injection patterns.

        Returns:
            {
                "safe": bool,
                "score": 0-100 (0=safe, 100=definitely malicious),
                "threats": [...],
                "summary": str,
                "sanitized": str,  # content with threats redacted
            }
        """
        if not content:
            return {"safe": True, "score": 0, "threats": [], "summary": "empty content"}

        threats = []
        sanitized = content

        # Check each pattern category
        for category, patterns in self.patterns.items():
            for pattern, severity in patterns:
                matches = pattern.finditer(content)
                for match in matches:
                    threat = {
                        "category": category,
                        "severity": severity,
                        "pattern": pattern.pattern[:60],
                        "match": match.group()[:100],
                        "position": match.start(),
                        "context": content[max(0, match.start()-30):match.end()+30][:120],
                    }
                    threats.append(threat)

                    # Redact in sanitized version
                    sanitized = sanitized[:match.start()] + "[REDACTED]" + sanitized[match.end():]

        # Check for base64-encoded instructions
        b64_threats = self._check_base64(content)
        threats.extend(b64_threats)

        # Check for unicode tricks
        unicode_threats = self._check_unicode(content)
        threats.extend(unicode_threats)

        # Calculate score
        score = self._calculate_score(threats)

        # Summary
        high_count = sum(1 for t in threats if t["severity"] == "HIGH")
        medium_count = sum(1 for t in threats if t["severity"] == "MEDIUM")

        if not threats:
            summary = "No injection patterns detected"
        elif high_count > 0:
            summary = f"DANGEROUS: {high_count} high-severity threats, {medium_count} medium"
        else:
            summary = f"SUSPICIOUS: {medium_count} medium-severity patterns detected"

        return {
            "safe": score < 30,
            "score": score,
            "threats": threats[:20],  # Cap at 20
            "threat_count": len(threats),
            "high_severity": high_count,
            "medium_severity": medium_count,
            "summary": summary,
            "source": source,
            "content_length": len(content),
            "content_hash": hashlib.sha256(content.encode()).hexdigest()[:16],
            "scanned_at": datetime.now(timezone.utc).isoformat(),
        }

    def _check_base64(self, content: str) -> List[Dict]:
        """Check for base64-encoded instruction payloads."""
        threats = []
        # Find base64-like strings (40+ chars of base64 alphabet)
        b64_pattern = re.compile(r'[A-Za-z0-9+/]{40,}={0,2}')
        for match in b64_pattern.finditer(content):
            try:
                decoded = base64.b64decode(match.group()).decode('utf-8', errors='ignore')
                # Check if decoded content contains injection patterns
                for category, patterns in self.patterns.items():
                    for pattern, severity in patterns:
                        if pattern.search(decoded):
                            threats.append({
                                "category": "encoded_injection",
                                "severity": "HIGH",
                                "pattern": f"base64 → {category}",
                                "match": f"[BASE64: {decoded[:60]}]",
                                "position": match.start(),
                                "context": f"Decoded: {decoded[:100]}",
                            })
                            break
            except Exception:
                pass  # Not valid base64, skip
        return threats

    def _check_unicode(self, content: str) -> List[Dict]:
        """Check for unicode direction override and invisible characters."""
        threats = []
        # Unicode direction overrides
        suspicious_chars = {
            '\u200b': 'zero-width space',
            '\u200c': 'zero-width non-joiner',
            '\u200d': 'zero-width joiner',
            '\u200e': 'left-to-right mark',
            '\u200f': 'right-to-left mark',
            '\u202a': 'left-to-right embedding',
            '\u202b': 'right-to-left embedding',
            '\u202c': 'pop directional formatting',
            '\u202d': 'left-to-right override',
            '\u202e': 'right-to-left override',
            '\u2060': 'word joiner',
            '\u2061': 'function application',
            '\ufeff': 'byte order mark',
        }

        for char, name in suspicious_chars.items():
            count = content.count(char)
            if count > 3:  # Allow a few BOM/joiners, flag excessive use
                threats.append({
                    "category": "unicode_manipulation",
                    "severity": "MEDIUM",
                    "pattern": f"excessive {name}",
                    "match": f"{count} instances of U+{ord(char):04X}",
                    "position": content.index(char),
                    "context": f"Found {count} hidden {name} characters",
                })
        return threats

    def _calculate_score(self, threats: List[Dict]) -> int:
        """Calculate danger score 0-100."""
        if not threats:
            return 0

        score = 0
        for t in threats:
            if t["severity"] == "HIGH":
                score += 25
            elif t["severity"] == "MEDIUM":
                score += 10

        # Cap at 100
        return min(score, 100)


# ============ Skill Entry Point ============
def run(content: str = "", source: str = "", file: str = "", **kwargs) -> dict:
    """
    Scan content for prompt injection.

    Args:
        content: Text to scan
        source: Where the content came from (URL, filename, etc.)
        file: Path to file to scan (alternative to content param)
    """
    if file and not content:
        try:
            with open(file) as f:
                content = f.read()
            source = source or file
        except Exception as e:
            return {"error": f"Cannot read file: {e}"}

    if not content:
        return {"error": "No content provided. Use content= or file= parameter."}

    guard = PromptGuard()
    return guard.scan(content, source)


# ============ CLI ============
if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Prompt Injection Defense")
    parser.add_argument("--text", default="", help="Text to scan")
    parser.add_argument("--file", default="", help="File to scan")
    parser.add_argument("--stdin", action="store_true", help="Read from stdin")
    parser.add_argument("--source", default="", help="Content source label")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    content = args.text
    if args.stdin:
        content = sys.stdin.read()
    elif args.file:
        with open(args.file) as f:
            content = f.read()

    if not content:
        print("Provide text via --text, --file, or --stdin")
        sys.exit(1)

    result = run(content=content, source=args.source or args.file)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        score = result["score"]
        safe = result["safe"]
        emoji = "✅" if safe else "🚩" if score >= 70 else "⚠️"

        print(f"\n{emoji} Score: {score}/100 — {'SAFE' if safe else 'DANGEROUS'}")
        print(f"  {result['summary']}")

        if result.get("threats"):
            print(f"\n  Threats ({result['threat_count']}):")
            for t in result["threats"][:10]:
                print(f"    [{t['severity']}] {t['category']}: {t['match'][:60]}")

        print()
