#!/usr/bin/env python3
"""
Sprint Audit Tool — Run after every build sprint / pomodoro session.
Checks all new/modified files for:
  1. SECURITY: Hardcoded secrets, API keys, tokens, passwords
  2. BUGS: Common Python/JS issues, syntax problems
  3. COPYRIGHT: Copied content, attribution issues, license concerns
  4. PII: Personal info leaks (emails, phones, addresses, real names of others)

Usage:
    python3 tools/sprint_audit.py                    # Audit uncommitted changes
    python3 tools/sprint_audit.py --all              # Audit entire repo
    python3 tools/sprint_audit.py --path path/to/dir # Audit specific directory
    python3 tools/sprint_audit.py --fix              # Auto-fix what's possible
"""

import os
import re
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

# ============================================================
# PATTERNS
# ============================================================

SECURITY_PATTERNS = [
    # API keys and tokens
    (r'(?i)(api[_-]?key|apikey)\s*[=:]\s*["\']?[A-Za-z0-9_\-]{20,}', "API key detected"),
    (r'(?i)(secret|token|password|passwd|pwd)\s*[=:]\s*["\'][^"\']{8,}', "Secret/token/password in plaintext"),
    (r'(?i)Bearer\s+[A-Za-z0-9_\-\.]{20,}', "Bearer token detected"),
    (r'sk-[A-Za-z0-9]{20,}', "OpenAI API key pattern"),
    (r'sk-ant-[A-Za-z0-9_\-]{20,}', "Anthropic API key pattern"),
    (r'ghp_[A-Za-z0-9]{36}', "GitHub personal access token"),
    (r'gho_[A-Za-z0-9]{36}', "GitHub OAuth token"),
    (r'xoxb-[0-9]{10,}', "Slack bot token"),
    (r'xoxp-[0-9]{10,}', "Slack user token"),
    (r'AKIA[0-9A-Z]{16}', "AWS access key"),
    # Connection strings
    (r'(?i)(mongodb|postgres|mysql|redis)://[^\s"\']+:[^\s"\']+@', "Database connection string with credentials"),
    (r'(?i)DSN\s*=\s*["\'][^"\']*password[^"\']*', "DSN with password"),
    # Private keys
    (r'-----BEGIN (RSA |EC |DSA )?PRIVATE KEY-----', "Private key detected"),
    (r'-----BEGIN OPENSSH PRIVATE KEY-----', "SSH private key detected"),
    # .env content in non-.env files
    (r'(?i)^[A-Z_]+=(?:sk-|ghp_|xox|AKIA|mongodb://)', ".env-style secret in code"),
]

BUG_PATTERNS = [
    # Python
    (r'except\s*:', "Bare except clause (catches everything including SystemExit)"),
    (r'eval\s*\(', "eval() usage (security risk, potential code injection)"),
    (r'exec\s*\(', "exec() usage (security risk)"),
    (r'os\.system\s*\(', "os.system() usage (use subprocess instead)"),
    (r'pickle\.loads?\s*\(', "pickle usage on untrusted data (deserialization attack)"),
    (r'yaml\.load\s*\([^)]*\)\s*$', "yaml.load without Loader (use safe_load)"),
    (r'__import__\s*\(', "Dynamic import (potential security issue)"),
    (r'shell\s*=\s*True', "subprocess shell=True (command injection risk)"),
    # JavaScript
    (r'innerHTML\s*=', "innerHTML assignment (XSS risk, use textContent)"),
    (r'document\.write\s*\(', "document.write (XSS risk)"),
    (r'\.html\s*\([^)]*\$', "jQuery .html() with variable (XSS risk)"),
    # General
    (r'(?<!\w)(?:FIXME|HACK|XXX)(?!\w)', "Unresolved FIXME/HACK marker"),
    (r'http://(?!localhost|127\.0\.0\.1|192\.168\.|0\.0\.0\.0|json-schema)', "HTTP (not HTTPS) URL"),
]

COPYRIGHT_PATTERNS = [
    # Direct copy indicators
    (r'(?i)copyright\s+\d{4}\s+(?!Kalani|Behike|behique)', "Copyright notice for someone else"),
    (r'(?i)all rights reserved', "All rights reserved notice (check if it's ours)"),
    (r'(?i)licensed under', "License reference (verify compatibility)"),
    (r'(?i)reproduced with permission', "Reproduction notice (verify we have permission)"),
    (r'(?i)adapted from|based on|derived from', "Attribution needed (verify source)"),
    # Long quoted passages (200+ chars, only flag truly long ones)
    (r'"[^"]{200,}"', "Very long quoted passage (200+ chars, check fair use)"),
    # Course/book content indicators
    (r'(?i)module \d+:\s+lesson \d+', "Course structure detected (check if transcribed content)"),
    (r'(?i)chapter \d+.*from\s+"', "Book chapter reference (verify fair use)"),
]

PII_PATTERNS = [
    # Email addresses (not our own, skip common safe ones)
    (r'[a-zA-Z0-9._%+-]+@(?!behike|behique|example|test|gumroad|anthropic|noreply|github|users\.noreply)[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', "Email address (not ours)"),
    # Phone numbers
    (r'(?<!\d)(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}(?!\d)', "Phone number detected"),
    # SSN pattern
    (r'\b\d{3}-\d{2}-\d{4}\b', "Possible SSN pattern"),
    # Credit card patterns
    (r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})\b', "Possible credit card number"),
    # IP addresses (internal/private are ok, flag public, skip well-known DNS and user-agents)
    (r'(?<!\d)(?!192\.168\.|10\.|172\.(?:1[6-9]|2[0-9]|3[01])\.|127\.0\.0\.1|0\.0\.0\.0|8\.8\.8\.8|1\.1\.1\.1|10_\d|10\.0)\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(?!\d)(?!.*(?:Mozilla|AppleWebKit|Chrome|Safari|Gecko|KHTML))', "Public IP address"),
    # Street addresses
    (r'\d{1,5}\s+\w+\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Way|Court|Ct)\b', "Street address detected"),
    # Real names with context (people other than Kalani)
    (r'(?i)(?:client|customer|user)\s+(?:name|called|named)\s*[=:]\s*["\'][A-Z][a-z]+\s+[A-Z][a-z]+', "Client/customer real name"),
]

# Files to always skip
SKIP_EXTENSIONS = {'.pyc', '.pyo', '.class', '.o', '.so', '.dylib', '.exe',
                   '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', '.webp',
                   '.mp3', '.mp4', '.wav', '.m4a', '.ogg', '.onnx', '.bin',
                   '.woff', '.woff2', '.ttf', '.eot',
                   '.zip', '.tar', '.gz', '.bz2', '.7z',
                   '.pdf', '.xlsx', '.docx', '.pptx'}

SKIP_DIRS = {'.git', 'node_modules', '__pycache__', '.venv', 'venv',
             'dist', 'build', '.next', '.cache', 'polymarket-data'}

SKIP_FILES = {'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml',
              'kokoro-v1.0.onnx', 'voices-v1.0.bin'}


# ============================================================
# SCANNER
# ============================================================

def get_changed_files():
    """Get list of uncommitted changed/new files from git."""
    try:
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True, text=True, cwd=os.getcwd()
        )
        files = []
        for line in result.stdout.strip().split('\n'):
            if not line.strip():
                continue
            status = line[:2].strip()
            filepath = line[3:].strip()
            # Handle renamed files
            if ' -> ' in filepath:
                filepath = filepath.split(' -> ')[1]
            # Remove quotes if present
            filepath = filepath.strip('"')
            if status != 'D':  # Skip deleted files
                files.append(filepath)
        return files
    except Exception:
        return []


def should_skip(filepath):
    """Check if file should be skipped."""
    path = Path(filepath)

    if path.suffix.lower() in SKIP_EXTENSIONS:
        return True
    if path.name in SKIP_FILES:
        return True
    for skip_dir in SKIP_DIRS:
        if skip_dir in path.parts:
            return True
    # Skip binary files
    try:
        with open(filepath, 'rb') as f:
            chunk = f.read(1024)
            if b'\x00' in chunk:
                return True
    except (OSError, IOError):
        return True
    return False


def scan_file(filepath, patterns, category):
    """Scan a single file against a set of patterns."""
    findings = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except (OSError, IOError):
        return findings

    for line_num, line in enumerate(lines, 1):
        for pattern, description in patterns:
            if re.search(pattern, line):
                # Skip false positives in comments about patterns
                if 'PATTERN' in line.upper() and category == 'SECURITY':
                    continue
                # Skip pattern definitions in this very file
                if 'sprint_audit.py' in filepath:
                    continue
                # Skip educational/example content in product guides
                if category == 'SECURITY':
                    lower = line.lower()
                    if any(x in lower for x in ['example', 'your-', 'replace', 'generate-a-',
                                                  'placeholder', 'your_', 'xxx', 'changeme',
                                                  'your-secret', 'your-api']):
                        continue
                # Skip 0.0.0.0 bind addresses (safe, not real PII)
                if category == 'PII' and '0.0.0.0' in line:
                    continue
                findings.append({
                    'file': filepath,
                    'line': line_num,
                    'category': category,
                    'description': description,
                    'content': line.strip()[:120],
                })
    return findings


def check_gitignore():
    """Verify .gitignore has essential entries."""
    essential = ['.env', '*.pem', '*.key', 'credentials*', '*_secret*',
                 '*.pyc', '__pycache__', 'node_modules']

    gitignore_path = Path('.gitignore')
    if not gitignore_path.exists():
        return [{'category': 'SECURITY', 'description': 'No .gitignore file found!',
                 'file': '.gitignore', 'line': 0, 'content': 'MISSING'}]

    content = gitignore_path.read_text()
    findings = []
    for entry in essential:
        if entry not in content:
            findings.append({
                'category': 'SECURITY',
                'description': f'.gitignore missing: {entry}',
                'file': '.gitignore',
                'line': 0,
                'content': f'Add "{entry}" to .gitignore',
            })
    return findings


def run_audit(files, verbose=True):
    """Run full audit on a list of files."""
    all_findings = []
    scanned = 0
    skipped = 0

    for filepath in files:
        if should_skip(filepath):
            skipped += 1
            continue
        if not os.path.isfile(filepath):
            continue

        scanned += 1
        all_findings.extend(scan_file(filepath, SECURITY_PATTERNS, 'SECURITY'))
        all_findings.extend(scan_file(filepath, BUG_PATTERNS, 'BUG'))
        all_findings.extend(scan_file(filepath, COPYRIGHT_PATTERNS, 'COPYRIGHT'))
        all_findings.extend(scan_file(filepath, PII_PATTERNS, 'PII'))

    # Check .gitignore
    all_findings.extend(check_gitignore())

    return all_findings, scanned, skipped


def print_report(findings, scanned, skipped):
    """Print formatted audit report."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Count by category
    counts = {}
    for f in findings:
        cat = f['category']
        counts[cat] = counts.get(cat, 0) + 1

    severity_order = ['SECURITY', 'PII', 'BUG', 'COPYRIGHT']
    severity_icons = {'SECURITY': 'CRITICAL', 'PII': 'HIGH', 'BUG': 'MEDIUM', 'COPYRIGHT': 'LOW'}

    print(f"\n{'='*60}")
    print(f"  SPRINT AUDIT REPORT")
    print(f"  {timestamp}")
    print(f"{'='*60}")
    print(f"  Files scanned: {scanned} | Skipped: {skipped}")
    print(f"  Total findings: {len(findings)}")

    for cat in severity_order:
        count = counts.get(cat, 0)
        if count > 0:
            print(f"  [{severity_icons[cat]}] {cat}: {count}")

    if not findings:
        print(f"\n  ALL CLEAR. No issues found.")
        print(f"{'='*60}\n")
        return

    print(f"{'='*60}\n")

    # Group by category
    for cat in severity_order:
        cat_findings = [f for f in findings if f['category'] == cat]
        if not cat_findings:
            continue

        print(f"  [{severity_icons[cat]}] {cat} ({len(cat_findings)} issues)")
        print(f"  {'-'*50}")

        for f in cat_findings:
            print(f"    {f['file']}:{f['line']}")
            print(f"      {f['description']}")
            if f['content'] and f['content'] != 'MISSING':
                # Redact potential secrets in output
                content = f['content']
                content = re.sub(r'(sk-|ghp_|xox|AKIA)[A-Za-z0-9_\-]+', r'\1***REDACTED***', content)
                print(f"      > {content[:100]}")
            print()

    print(f"{'='*60}")

    # Verdict
    critical = counts.get('SECURITY', 0) + counts.get('PII', 0)
    if critical > 0:
        print(f"  VERDICT: BLOCK COMMIT. Fix {critical} critical issues first.")
    else:
        print(f"  VERDICT: SAFE TO SAVE. {len(findings)} non-critical items to review.")
    print(f"{'='*60}\n")


def save_report(findings, scanned, skipped):
    """Save audit report to file."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_dir = Path(os.path.expanduser('~/behique/Ceiba/audit-reports'))
    report_dir.mkdir(parents=True, exist_ok=True)

    report = {
        'timestamp': datetime.now().isoformat(),
        'files_scanned': scanned,
        'files_skipped': skipped,
        'total_findings': len(findings),
        'findings': findings,
        'verdict': 'BLOCK' if any(f['category'] in ('SECURITY', 'PII') for f in findings) else 'PASS',
    }

    report_file = report_dir / f'audit_{timestamp}.json'
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"  Report saved: {report_file}")


# ============================================================
# MAIN
# ============================================================

def main():
    args = sys.argv[1:]

    if '--help' in args or '-h' in args:
        print(__doc__)
        return

    # Determine which files to scan
    if '--all' in args:
        # Scan entire repo
        files = []
        for root, dirs, filenames in os.walk('.'):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for fname in filenames:
                files.append(os.path.join(root, fname))
        print(f"  Scanning entire repository...")
    elif '--path' in args:
        idx = args.index('--path')
        if idx + 1 < len(args):
            target = args[idx + 1]
            files = []
            if os.path.isfile(target):
                files = [target]
            elif os.path.isdir(target):
                for root, dirs, filenames in os.walk(target):
                    dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
                    for fname in filenames:
                        files.append(os.path.join(root, fname))
            print(f"  Scanning: {target}")
        else:
            print("  Error: --path requires a path argument")
            return
    else:
        # Default: scan uncommitted changes
        files = get_changed_files()
        if not files:
            print("  No uncommitted changes to audit. Use --all for full scan.")
            return
        print(f"  Scanning {len(files)} changed files...")

    # Run audit
    findings, scanned, skipped = run_audit(files)

    # Print report
    print_report(findings, scanned, skipped)

    # Save report
    save_report(findings, scanned, skipped)

    # Exit code
    critical = sum(1 for f in findings if f['category'] in ('SECURITY', 'PII'))
    sys.exit(1 if critical > 0 else 0)


if __name__ == '__main__':
    main()
