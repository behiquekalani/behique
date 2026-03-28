# Full Security Audit Report
# Date: 2026-03-22
# Auditor: Ceiba Security Agent (Claude Opus 4.6)
# Scope: /Users/kalani/behique (entire project directory)
# Classification: CONFIDENTIAL

---

## EXECUTIVE SUMMARY

**Total findings: 47**

| Severity | Count |
|----------|-------|
| CRITICAL | 5 |
| HIGH | 12 |
| MEDIUM | 18 |
| LOW | 12 |

**Immediate action required on 5 CRITICAL items before any product goes public.**

---

## SECTION 1: CRITICAL FINDINGS (Fix Immediately)

### CRIT-01: Live API Keys in .env File (Unencrypted on Disk)

**File:** `/Users/kalani/behique/.env`
**Severity:** CRITICAL
**Status:** .env is NOT tracked by git (good), but plaintext on disk

The following live credentials are stored in plaintext:
- `TELEGRAM_TOKEN=8620592974:AAH...lCM` (full Telegram bot token)
- `OPENAI_API_KEY=sk-proj-yXv...moA` (full OpenAI API key, ~140 chars)
- `NOTION_SECRET=ntn_2150...bVl` (full Notion integration secret)
- `NOTION_DATABASE_ID=323501e0...` (full Notion database ID)

**Risk:** If this machine is compromised, lost, or accessed by anyone, they get full control of:
- Your Telegram bot (BehiqueBot)
- Your OpenAI account (billing access)
- Your Notion database (all ideas, personal data)

**Remediation:**
1. Rotate ALL keys immediately (Telegram via @BotFather, OpenAI at platform.openai.com, Notion at integrations page)
2. Use a secrets manager (macOS Keychain, 1Password CLI, or `age` encryption)
3. Set `.env` permissions to 600 (currently correct: `-rw-------`)
4. Never store Notion database IDs alongside secrets

---

### CRIT-02: CEIBA-FINANCE-BRIEFING.txt Contains Full Financial Profile

**File:** `/Users/kalani/behique/CEIBA-FINANCE-BRIEFING.txt`
**Severity:** CRITICAL
**Git tracked:** NO (untracked, but on disk in the repo root)

This file contains:
- Exact salary: $3,000/mo
- All credit card balances with APRs (Discover $15,008.89 at 28.24%, Best Buy $5,967.08 at 30.49%, Chase $6,636.91 at 28.24%)
- Total debt: $35,614.18
- Student loan balance: $8,001.30
- Paycheck schedule and split
- Personal loans owed BY others TO Kalani (Daniel: $1,000, Mary: $1,000)
- Monthly expense breakdown (car payment, insurance, internet, etc.)

**Risk:** Identity theft, social engineering, financial exploitation. This is a full financial dossier.

**Remediation:**
1. Move to an encrypted location outside the repo (e.g., encrypted disk image or 1Password)
2. Add to `.gitignore`: `CEIBA-FINANCE-BRIEFING.txt`, `*FINANCE*`, `*BRIEFING*`
3. Delete from the repo directory entirely

---

### CRIT-03: Full Name + Medical Info Committed to Git in CLAUDE.md

**File:** `/Users/kalani/behique/CLAUDE.md` (GIT TRACKED)
**Severity:** CRITICAL

This file is committed to git and contains:
- Full legal name: "Kalani Andre Gomez Padin"
- ADHD diagnosis: "He has ADHD (diagnosed, working with a psychologist)"
- Personality type: "INFJ"
- School: "Computer engineering student in Puerto Rico"
- Nationality/location: Puerto Rico
- Psychological framework details (psychologist's framework)
- Family motivation details
- Behavioral patterns (avoidance, going quiet)

**Risk:** If this repo is ever made public (even accidentally), this is a full personal dossier including protected health information (ADHD diagnosis).

**Remediation:**
1. Remove personal identifying information from CLAUDE.md
2. Replace "Kalani Andre Gomez Padin" with a pseudonym or just "the user"
3. Remove the ADHD diagnosis mention -- this is protected health information
4. Move psychological details to a file that is gitignored
5. Consider whether CLAUDE.md should be gitignored entirely

---

### CRIT-04: shared-memory.md Contains PII + Third Party Names

**File:** `/Users/kalani/behique/shared-memory.md` (untracked but synced via Syncthing)
**Severity:** CRITICAL

Contains:
- Girlfriend's full name: "Yamilet" with course details (ENGL1010-80)
- Statement that "Kalani manages her coursework"
- Internal machine IPs (192.168.0.151, 192.168.0.152)
- SSH usernames (kalani@192.168.0.152)
- Detailed infrastructure map (all three machines, their roles, their IPs)

**Risk:** Syncthing syncs this across machines. If any machine is compromised, attacker gets full network topology. Yamilet's name and course info is third-party PII shared without her consent.

**Remediation:**
1. Remove Yamilet's full name and course details
2. Remove specific IPs from synced files
3. Never mention managing someone else's coursework in a shared file

---

### CRIT-05: student-essays-pet-peeves.md Contains Third-Party Student Names

**File:** `/Users/kalani/behique/Ceiba/projects/content-empire/student-essays-pet-peeves.md`
**Severity:** CRITICAL

Contains:
- "Yamilet Diaz Diaz" with timestamp (Mar 16, 12:16 AM)
- Likely other student names from a class discussion

**Risk:** This is in the content-empire directory, which is product-adjacent. If this file is ever distributed or the repo goes public, it exposes a third party's full legal name without consent. FERPA implications if this is from a university context.

**Remediation:**
1. Anonymize all student names immediately
2. Move out of the content-empire directory
3. Add to .gitignore if not already

---

## SECTION 2: HIGH SEVERITY FINDINGS

### HIGH-01: Internal Network IPs in Git-Tracked Files

**Files affected (committed to git):**
- `modules/classifier.py:9` -- `OLLAMA_HOST = "http://192.168.0.151:11434"`
- `modules/routing.py:26` -- `OLLAMA_HOST = "http://192.168.0.151:11434"`
- `bridge/dispatch.sh:7-9` -- `BRIDGE_URL`, `OLLAMA_URL`, `COBO_IP` all hardcoded to `192.168.0.151`
- `bridge/COMPUTER2_MIND.md:80` -- "IP: 192.168.0.151"
- `Ceiba/04-Patterns/observations.md` -- various IP references

**Risk:** Reveals internal network topology. An attacker who gains network access knows exactly where to find the bridge server (port 9876), Ollama (port 11434), and n8n (port 5678).

**Remediation:**
1. Use environment variables for ALL IP addresses. Change hardcoded IPs to `os.getenv("OLLAMA_HOST", "http://localhost:11434")`
2. Never commit internal IPs to git

---

### HIGH-02: Internal IPs in Sellable Product Files

**Files:**
- `products/ai-employee-guide.md:262` -- "Kalani already uses it" (personal reference)
- `products/ai-employee-guide.md:1646` -- `"http://192.168.0.153:11434"` (hardcoded real IP)
- `products/es/guia-empleado-ia.md:1645` -- same IP `192.168.0.153`
- `products/ai-chatbot-guide.md:563` -- `http://192.168.0.100:9877` (example IP, acceptable)
- `products/es/guia-chatbot-ia.md:563` -- same example IP

**Risk:** The 192.168.0.153 IP on line 1646 of ai-employee-guide.md is labeled "Future node" which means it is a REAL planned IP from Kalani's network, not a generic example. The `192.168.X.100` references in the Spanish version are properly genericized (good), but the English version leaks a real IP.

**Remediation:**
1. Change `192.168.0.153` to `192.168.X.103` in both ai-employee-guide.md and guia-empleado-ia.md
2. Remove "Kalani already uses it" from the Notion table row (line 262 EN, 261 ES)
3. Change to "Already widely used" or similar

---

### HIGH-03: kalani1337@gmail.com Embedded in Every Git Commit

**Source:** `git config user.email` returns `kalani1337@gmail.com`
**Severity:** HIGH

Every commit in the repository's history contains this personal email. If the repo is ever pushed to a public remote (even briefly), this email is permanently exposed.

**Remediation:**
1. For public-facing repos, use a noreply email (GitHub provides `username@users.noreply.github.com`)
2. For this repo, if it stays private, this is acceptable but noted

---

### HIGH-04: CORS Wildcard in Transcription SaaS

**File:** `/Users/kalani/behique/tools/transcription-saas/app.py:50`
```python
allow_origins=["*"],
allow_credentials=True,
```

**Risk:** `allow_origins=["*"]` combined with `allow_credentials=True` is a classic CORS misconfiguration. Any website can make authenticated requests to this API. This enables CSRF attacks and data exfiltration.

**Remediation:**
1. Replace `"*"` with specific allowed origins
2. Never combine `allow_origins=["*"]` with `allow_credentials=True`

---

### HIGH-05: Bridge Token Read from Unprotected File

**File:** `/Users/kalani/behique/bridge/dispatch.sh:6`
```bash
BRIDGE_TOKEN="${BRIDGE_TOKEN:-$(cat ~/.behique_bridge_token 2>/dev/null)}"
```

**Risk:** The bridge token file `~/.behique_bridge_token` permissions are unknown. If readable by other users, any local user can authenticate to the bridge server and execute commands on Cobo.

**Remediation:**
1. Verify `~/.behique_bridge_token` has permissions `600`
2. Consider using macOS Keychain instead of a file

---

### HIGH-06: Full Legal Name as Author in All Sellable Products

**Files (all committed/distributable):**
- `products/behike-method-v2.md:4` -- "By Kalani Andre Gomez Padin"
- `products/behike-method-content-system.md:4` -- "By Kalani Andre Gomez Padin"
- `products/ecommerce-playbook-v2.md:4` -- copyright line with full name
- `products/es/guia-ecommerce.md:6` -- copyright line with full name
- `products/es/guia-empleado-ia.md:1840` -- sign-off with full name
- `products/ai-employee-guide.md:1841` -- sign-off with full name

**Risk:** This is an intentional branding decision, but the full legal name "Kalani Andre Gomez Padin" combined with "computer engineering student in Puerto Rico" and ADHD disclosure in behike-method-v2.md creates a very detailed public profile.

**Assessment:** ACCEPTABLE if intentional, but noted. The ADHD disclosure in a sellable product is a personal decision that should be made deliberately, not accidentally.

---

### HIGH-07: ADHD Diagnosis Disclosed in Sellable Products

**Files:**
- `products/behike-method-v2.md:22,76,160-163,225-255` -- Entire Chapter 3 is about ADHD. Explicitly states "if you have ADHD, whether diagnosed or suspected"
- `themes/behike-store/landing-pages/behike-method-v2.html:181` -- "I have ADHD"
- `themes/behike-store/landing-pages/behike-method.html` -- Multiple ADHD references
- `Ceiba/faces/behike-hub.html:836-848` -- "Diagnosed ADHD. Working with a psychologist."

**Risk:** This is protected health information being disclosed publicly. In the Behike Method product this appears intentional and is part of the brand identity. However, the behike-hub.html file explicitly mentions "Working with a psychologist" which is more personal than the product needs.

**Assessment:** Products (behike-method) -- ACCEPTABLE (intentional brand disclosure). Faces/internal tools -- REMOVE psychologist mention.

---

### HIGH-08: Yamilet's Full Name in Product-Adjacent Files

**Files:**
- `Ceiba/projects/content-empire/student-essays-pet-peeves.md:71` -- "Yamilet Diaz Diaz"
- `Ceiba/projects/content-empire/instagram-content-batch-2.md:137` -- "My girlfriend asked me..."
- `Ceiba/projects/content-empire/es/instagram-contenido-lote-2.md:138` -- "Mi novia me pregunto..."
- `Ceiba/projects/ai-marketplace/VISION_UPDATES.md:29` -- "his girlfriend Yami"

**Risk:** Third-party PII in content drafts. If these files are distributed or the repo goes public, Yamilet's identity and relationship status are exposed.

**Remediation:**
1. Replace "Yamilet Diaz Diaz" with anonymized name
2. In Instagram content, "my girlfriend" is fine but remove full names from all drafts

---

### HIGH-09: Bridge Command Execution Without Input Sanitization

**File:** `/Users/kalani/behique/bridge/dispatch.sh:31`
```bash
ESCAPED_PROMPT=$(echo "$PROMPT" | sed 's/"/\\"/g')
```

The `sed` escaping is insufficient. The prompt is user-supplied and injected into a JSON string that gets sent as a command to the bridge server. A malicious prompt containing backticks, `$()`, or other shell metacharacters could achieve command injection.

**Remediation:**
1. Use `jq` for JSON construction instead of string interpolation
2. Add input validation/sanitization before constructing the command

---

### HIGH-10: os.system() with Unsanitized Input

**File:** `/Users/kalani/behique/tools/carousel_generator.py:419`
```python
os.system(f"open '{filepath}'")
```

**Risk:** If `filepath` contains single quotes or shell metacharacters, this enables command injection.

**Remediation:** Use `subprocess.run(["open", filepath])` instead.

---

### HIGH-11: Chatbot Instructions Expose Internal Architecture

**File:** `/Users/kalani/behique/bridge/cobo-chatbot-instructions.md`
- Line 74: Identifies "Kalani Andre" as the builder
- Line 211: Hardcodes `http://192.168.0.151:9877/chat` as the widget endpoint
- Contains full product catalog and pricing

**Risk:** This file maps the internal chatbot architecture. If the chatbot is publicly accessible, the instructions should not expose internal IPs.

**Remediation:** Use environment variables for the API endpoint.

---

### HIGH-12: Instagram Content Contains Personal Relationship Details

**File:** `instagram-content-batch-2.md:137`
Content script: "My girlfriend asked me, 'When does this start making money?'"

**Risk:** While this is authentic content marketing, it exposes a real relationship dynamic and financial pressure. Combined with Yamilet's name elsewhere, this creates a traceable personal narrative.

**Assessment:** ACCEPTABLE as content if intentional, but ensure no full names appear in published versions.

---

## SECTION 3: MEDIUM SEVERITY FINDINGS

### MED-01: Internal Machine Names in Faces/Dashboards
Ceiba, Cobo, Hutia machine names with IPs appear in:
- `Ceiba/faces/agent-faces.html:391` -- "Windows (192.168.0.151)"
- `Ceiba/faces/ceiba-hq.html:2021-2034` -- All three machine endpoints
- `Ceiba/faces/unified-hub.html:1610` -- Cobo IP
- `Ceiba/faces/api/dashboard.json:124-140` -- All three IPs
These are internal tools but if served publicly, they leak infrastructure.

### MED-02: "Kalani" Name in Face/Dashboard Files
Player name "Kalani" appears in quest-dashboard.html, unified-hub.html, ceiba-hq.html, pipboy-quest-log.html. These are personal tools, but if accidentally served or screenshotted, they identify the operator.

### MED-03: behikeai@gmail.com in Sellable Products
Contact email appears in solopreneur-os.md, el-metodo-behike.md (both EN and ES). This is intentional (brand email for permissions), but noted.

### MED-04: kalaniandrez Instagram in Products
@kalaniandrez links appear in: bio-link.html, landing-pages/index.html, claude-code-course.html, theme-bundle.html, behike-hub.html. Intentional branding, acceptable.

### MED-05: Landing Page localStorage Usage Without Encryption
Products use localStorage for user data:
- automation-audit-template.html stores audit results
- cash-flow-dashboard.html stores financial data
- personal-budget-template.html stores budget data
- meditation-app.html stores session history
This data is unencrypted and accessible to any JavaScript on the same origin.

### MED-06: innerHTML Usage in Products (XSS Surface)
Multiple products use innerHTML with dynamically constructed content:
- cash-flow-dashboard.html (30+ instances)
- automation-audit-template.html (8+ instances)
- budget-template.html
Since these are standalone HTML products (no server, no user input from external sources), the XSS risk is LOW in practice. The data comes from the user's own localStorage input. However, if these templates are ever embedded in a multi-tenant environment, innerHTML should be replaced with textContent + DOM construction.

### MED-07: Hardcoded Ollama IPs in BehiqueBot Modules
`modules/classifier.py` and `modules/routing.py` hardcode `192.168.0.151` as fallback. These are deployed on Railway where the fallback will fail silently, but they reveal infrastructure.

### MED-08: Reel Pipeline Uses Hardcoded Ollama IP
`tools/reel-pipeline/translate_stories.py:24` -- `"http://192.168.0.151:11434"`

### MED-09: Hutia Image Gen Tool Has Hardcoded IP
`tools/hutia_image_gen.py:21` -- `HUTIA_HOST = "192.168.0.152"`

### MED-10: COMPUTER2_MIND.md Contains Full System Architecture
`bridge/COMPUTER2_MIND.md` is git-tracked and contains:
- Complete memory stack file map
- Credential file locations (.ceiba-config)
- All env var names (TELEGRAM_BOT_TOKEN, OPENAI_API_KEY, etc.)
- Network topology
- Project priorities and financial status

### MED-11: Quest Dashboard References "eBay API keys"
`Ceiba/faces/quest-dashboard.html:1043` -- task "Get eBay API keys (Prod + Sandbox)" reveals platform usage.

### MED-12: Professor Eval Review HTML Contains kalani Reference
`dashboards/professor-eval-review.html:649` -- contains reference to kalani email.

### MED-13: Ceiba Backups Contain Calendar ID
`Ceiba/backups/session8_handoff_20260317.md:11` -- "Calendar ID: kalani1337@gmail.com"

### MED-14: HUTIA_REBUILD_PLAN Contains SSH Credentials Pattern
`Ceiba/HUTIA_REBUILD_PLAN.md` -- Contains `ssh kalani@192.168.0.152` and `ssh-copy-id` commands. Not actual keys, but reveals SSH user and infrastructure.

### MED-15: Observation Notes Contain Personal Behavioral Patterns
`Ceiba/04-Patterns/observations.md` (git-tracked) contains behavioral analysis: "sent girlfriend update," avoidance patterns, etc.

### MED-16: Content Scripts Reference Real Relationship Dynamics
`content-empire/dan-koe-opb-foundations.md` contains personal details about girlfriend, family time, gift-giving patterns.

### MED-17: Account Strategy File Lists All Instagram Accounts
`content-empire/account-strategy.md` lists all accounts (@behikeai, @kalaniandrez, @dulc3recuerdo, @s0ftrewind) with strategy details.

### MED-18: nixpacks.toml Exists (Railway Deployment Config)
`/Users/kalani/behique/nixpacks.toml` -- reveals deployment platform (Railway).

---

## SECTION 4: LOW SEVERITY FINDINGS

### LOW-01: .env.example Lists Available Secret Types
Shows SHRINE_THEME_TOKEN, SHRINE_LITE_TOKEN, SHOPIFY_DOMAIN, SHOPIFY_STOREFRONT_TOKEN as available variables. Not secrets themselves, but reveals what services are used.

### LOW-02: Git User Config Exposes Personal Email
`git config user.email` = `kalani1337@gmail.com`. All commits carry this.

### LOW-03: Log Files in output/ Directory
Multiple scraper log files exist in `/Users/kalani/behique/output/`. These are gitignored but contain operational data.

### LOW-04: SQLite Databases on Disk
- `cache/trends_cache.db`
- `vectors.db`
- `.claude/memory.db`
- `.swarm/memory.db`
These contain operational data and should be included in backup encryption strategy.

### LOW-05: Debug HTML Files in TrendsReports_Playwright/
Google Trends debug pages contain no PII but reveal product research methodology.

### LOW-06: Instagram Poster Lists All Accounts
`tools/instagram_poster.py:45` -- ACCOUNTS list includes all four accounts.

### LOW-07: Reddit Scraped IDs File
`tools/.reddit_scraped_ids.json` -- reveals Reddit scraping activity.

### LOW-08: Roblox Guide Uses "Kalani" as Example
`products/roblox-builders-guide.md:241` -- `greetPlayer("Kalani")`. Minor but unnecessary.

### LOW-09: eBay Listing JSON Files Contain Product Research
Listing files in `tools/ebay-listing-assistant/listings/` contain pricing strategy data.

### LOW-10: Faces Directory Not in .gitignore
The faces/ directory (Ceiba/faces/) contains personal dashboards with names, IPs, and infrastructure data. Some files are git-tracked.

### LOW-11: .claude Directory Not Fully Gitignored
`.claude/memory.db` contains Claude session data. The .gitignore handles `.claude/*` but other worktrees may not.

### LOW-12: Blueprint Builder Products Are Clean
All blueprint HTML products in `tools/blueprint-builder/` pass security audit. No PII, no secrets, no IPs. Good.

---

## SECTION 5: CYBERSECURITY ASSESSMENT

### 5.1 Secrets Management

| Item | Status | Notes |
|------|--------|-------|
| .env file | NOT in git | Correct. Permissions 600. |
| .env.example | In git | Correct. No values. |
| Bridge token | File-based (~/.behique_bridge_token) | Check permissions |
| API keys in source code | NONE found | Clean |
| SSH keys in repo | NONE found | Clean |
| JWT tokens | NONE found | Clean |
| Database connection strings | NONE found | Clean |
| Shrine theme license keys | NOT in any file | Clean (in .env only) |

### 5.2 Git History

| Check | Result |
|-------|--------|
| .env ever committed | NO |
| API keys in commits | NO (checked with git log -S) |
| Secrets in non-.env files | NO |

### 5.3 Code Security

| Vulnerability | Files | Severity |
|---------------|-------|----------|
| Command injection (dispatch.sh) | bridge/dispatch.sh | HIGH |
| os.system() injection | tools/carousel_generator.py | HIGH |
| CORS wildcard + credentials | tools/transcription-saas/app.py | HIGH |
| innerHTML (XSS surface) | Multiple product HTML files | LOW (standalone) |
| subprocess without shell=False | main.py, modules/transcribe_command.py | LOW (controlled input) |

### 5.4 Network Exposure

| IP | Appears In | Git Tracked |
|----|-----------|-------------|
| 192.168.0.145 (Ceiba) | faces/api/dashboard.json | untracked |
| 192.168.0.151 (Cobo) | 30+ files | YES (multiple) |
| 192.168.0.152 (Hutia) | 10+ files | YES (some) |
| 192.168.0.153 (Future) | 2 product files | untracked |

---

## SECTION 6: COMPLIANCE STATUS

### 6.1 Data Protection (GDPR-Adjacent)

| Requirement | Status | Notes |
|-------------|--------|-------|
| Third-party consent | FAIL | Yamilet's full name used without documented consent |
| Data minimization | FAIL | Finance briefing contains excessive personal data |
| Right to erasure | N/A | No user data collection in products |
| Privacy notice | MISSING | Products collect localStorage data without privacy notice |

### 6.2 Product Readiness for Public Sale

| Product | PII Issues | Security Issues | Ready? |
|---------|-----------|-----------------|--------|
| Behike Method v2 | Full name (intentional), ADHD (intentional) | None | YES (if disclosures are intentional) |
| AI Employee Guide | "Kalani already uses it" (line 262), real IP 192.168.0.153 | None | FIX 2 ITEMS |
| AI Chatbot Guide | Example IP 192.168.0.100 (acceptable) | None | YES |
| Solopreneur OS | behikeai@gmail.com (intentional) | None | YES |
| Cash Flow Dashboard | None | localStorage unencrypted | YES (add privacy note) |
| Personal Budget Template | None | localStorage unencrypted | YES (add privacy note) |
| Automation Audit Template | None | localStorage unencrypted | YES (add privacy note) |
| Meditation App | None | localStorage unencrypted | YES |
| eBay Dropshipping Guide | None | None | YES |
| Amazon FBA Guide | None | None | YES |
| Roblox Builders Guide | "Kalani" as example name | None | FIX 1 ITEM |
| Landing Page Template | None | None | YES |
| Bio Link | @kalaniandrez (intentional) | None | YES |
| Blueprint Builder products | None | None | YES |
| Ecommerce Playbook v2 | Full name in copyright (intentional) | None | YES |
| Self-Hosted Store Guide | None | None | YES |
| AI News Tracker Guide | None | None | YES |
| Cover Images HTML | None | None | YES |
| Lumina (product brief) | None | None | YES |

### 6.3 Spanish (/es/) Product Variants

| Product | PII Issues | Ready? |
|---------|-----------|--------|
| El Metodo Behike | Full name (intentional) | YES |
| Guia Empleado IA | "Kalani ya la usa" (line 261), real IP 192.168.0.153 (line 1645), full name sign-off | FIX 3 ITEMS |
| Guia Chatbot IA | Example IP (acceptable) | YES |
| Solopreneur OS (ES) | behikeai@gmail.com (intentional) | YES |
| Guia Ecommerce | Copyright with full name (intentional) | YES |
| Guia Amazon FBA | None | YES |
| Guia eBay Dropshipping | None | YES |
| Guia Tienda Autoalojada | None | YES |
| Guia Rastreador Noticias IA | None | YES |

---

## SECTION 7: LANDING PAGES AUDIT

| Landing Page | Issues Found | Status |
|-------------|-------------|--------|
| index.html | "Built by Kalani Andre" + @kalaniandrez link | INTENTIONAL |
| behike-method.html | ADHD references (intentional branding) | CLEAN |
| behike-method-v2.html | "I have ADHD" (intentional), "comp-sci student in Puerto Rico" | INTENTIONAL |
| solopreneur-os.html | ADHD references (acceptable, generic) | CLEAN |
| ai-chatbot-guide.html | None | CLEAN |
| ebay-dropshipping-guide.html | None | CLEAN |
| amazon-fba-guide.html | None | CLEAN |
| 3d-fashion-guide.html | None | CLEAN |
| budget-template.html | None | CLEAN |
| roblox-builders-guide.html | None | CLEAN |
| claude-code-course.html | @kalaniandrez link | INTENTIONAL |
| lumina.html | ADHD Focus Mode (product feature, not personal) | CLEAN |
| theme-bundle.html | @kalaniandrez link | INTENTIONAL |
| automation-audit.html | None | CLEAN |
| ai-employee-guide.html | "kalani@ceiba" terminal prompt | LOW RISK |
| chat-widget.js | None | CLEAN |
| settings-widget.js | None | CLEAN |
| Preview pages | Locked content previews, no PII | CLEAN |

---

## SECTION 8: THEMES DIRECTORY AUDIT

All Shopify themes checked: behike-store, behike-starter, behike-pro, behike-empire, gumroad-starter, gumroad-pro, gumroad-empire, shrine-premium, shrine-lite, dermatify.

**Result:** CLEAN. No API keys, no personal information, no hardcoded credentials. Standard Shopify Dawn-based themes with password modal CSS (standard Shopify feature, not actual passwords).

---

## SECTION 9: PRIORITIZED ACTION ITEMS

### Immediate (Before ANY product launch):

1. **Rotate all API keys** in `.env` (Telegram, OpenAI, Notion). Consider them compromised since they have been in plaintext.

2. **Fix ai-employee-guide.md** (EN + ES):
   - Line 262 EN / 261 ES: Change "Kalani already uses it" to "Widely adopted"
   - Line 1646 EN / 1645 ES: Change `192.168.0.153` to `192.168.X.103`

3. **Move CEIBA-FINANCE-BRIEFING.txt** out of the repo to an encrypted location. Add `*FINANCE*` and `*BRIEFING*` to .gitignore.

4. **Anonymize student-essays-pet-peeves.md** -- Remove "Yamilet Diaz Diaz" and any other real student names.

5. **Fix roblox-builders-guide.md:241** -- Change `greetPlayer("Kalani")` to `greetPlayer("Player1")`.

### This Week:

6. Replace hardcoded IPs in modules/classifier.py and modules/routing.py with env var defaults (localhost, not 192.168.0.151).

7. Fix CORS in tools/transcription-saas/app.py -- remove wildcard origin or remove allow_credentials.

8. Fix bridge/dispatch.sh -- use `jq` for JSON construction instead of string interpolation.

9. Fix tools/carousel_generator.py:419 -- replace `os.system()` with `subprocess.run()`.

10. Review CLAUDE.md -- consider removing or gitignoring the "WHO KALANI IS" section with medical details.

### Before Going Public (GitHub/Open Source):

11. Remove all internal IPs from git-tracked files.
12. Remove Yamilet references from all content drafts.
13. Remove Ceiba/04-Patterns/observations.md from git tracking (personal behavioral data).
14. Remove bridge/COMPUTER2_MIND.md from git tracking (full system architecture).
15. Change git email to a noreply address for public repos.
16. Review all Ceiba/faces/ files -- they contain personal dashboards with names and IPs.

---

## SECTION 10: WHAT PASSED

The following areas are secure:
- .env is properly gitignored and has correct file permissions (600)
- No API keys or secrets found in any source code file
- No SSH keys in the repository
- No JWT tokens in any file
- No database connection strings exposed
- Shrine theme license keys are NOT in any tracked file
- All Shopify themes are clean
- All blueprint products are clean
- Landing pages contain no security vulnerabilities
- All product HTML files use localStorage for user-owned data only (no server communication)
- The .gitignore correctly excludes legal/correspondence/, legal/contracts/, .env files, biography files, and other sensitive directories
- No private keys found anywhere in the repository

---

## APPENDIX A: Files Scanned

Total files examined: 200+ across:
- Ceiba/projects/content-empire/products/ (40 files including /es/)
- themes/behike-store/landing-pages/ (20 files)
- tools/*.py (35 files)
- Ceiba/faces/*.html (20 files)
- bridge/ (8 files)
- legal/ (18 files)
- themes/ (11 theme directories)
- modules/*.py (all bot modules)
- main.py
- .env, .env.example, .gitignore
- All config files (nixpacks.toml, package.json)

## APPENDIX B: Scan Methodology

1. Pattern-based grep for API keys, tokens, secrets (regex matching AWS, OpenAI, GitHub, GitLab patterns)
2. Full-text search for personal names (Kalani, Gomez, Padin, Yamilet, Diaz, Anabel, Octavio)
3. Network IP pattern matching (192.168.x.x, 10.x.x.x, 172.16-31.x.x)
4. Email pattern matching (@gmail, @hotmail, etc.)
5. Medical/health term matching (ADHD, psychologist, therapy, diagnosis)
6. Financial data pattern matching (debt, APR, salary, SSN)
7. Git history audit (git log -S for secrets, git ls-files for tracked sensitive files)
8. Code security patterns (exec, subprocess, eval, innerHTML, CORS, shell=True)
9. File permission checks
10. localStorage/sessionStorage usage audit
11. Private key detection (BEGIN PRIVATE KEY patterns)
12. JWT token detection (eyJ pattern)
13. Database connection string detection (mongodb://, postgres://, etc.)

---

*Report generated: 2026-03-22*
*Auditor: Ceiba Security Agent (Claude Opus 4.6, 1M context)*
*Scope: Full repository audit (/Users/kalani/behique)*
*Classification: CONFIDENTIAL -- Do not distribute*
