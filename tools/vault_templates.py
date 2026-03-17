#!/usr/bin/env python3
"""
Vault Template System — Standardized templates for vault file types.

Creates properly structured vault files with YAML frontmatter,
correct wiki links, breadcrumbs section, and type-specific content.

Templates:
  project   — Active project with status, file map, breadcrumbs
  tool      — Tool/script documentation
  decision  — Architecture/strategy decision record
  pattern   — Behavioral or technical pattern
  session   — Session log (usually auto-generated)
  design    — Architecture/design document
  check-in  — Emotional/progress check-in

Usage:
    python3 vault_templates.py project "My New Project"
    python3 vault_templates.py tool "TOOL_My_Tool"
    python3 vault_templates.py decision "DEC_Why_We_Chose_X"
    python3 vault_templates.py pattern "PAT_Some_Pattern"
    python3 vault_templates.py --list                      # show all templates
    python3 vault_templates.py --apply-missing             # add templates to stub files
"""

import os
import sys
import argparse
from datetime import datetime

BEHIQUE = os.path.expanduser("~/behique")
CEIBA = os.path.join(BEHIQUE, "Ceiba")

# Where each type lives
TYPE_DIRS = {
    "project": "01-Projects",
    "tool": "05-Knowledge/tools",
    "decision": "04-Patterns/decisions",
    "pattern": "04-Patterns",
    "session": "06-Sessions",
    "design": "06-Designs",
    "check-in": "03-Check-ins",
    "goal": "02-Goals",
    "knowledge": "05-Knowledge",
}

TODAY = datetime.now().strftime("%Y-%m-%d")


def template_project(name, slug):
    return f"""---
title: "{name}"
type: project
status: planning
priority: medium
tools: []
systems: []
patterns: []
decisions: []
tags: [project]
created: {TODAY}
---

# {name}
**Status:** 📋 Planning
**Priority:** MEDIUM
**Started:** {TODAY}

---

## What It Does
> One-paragraph description of what this project accomplishes.

## Why It Matters
> Connect to a goal: → [[02-Goals/Q3-2026]]

## Current State ({TODAY})
- [ ] First milestone
- [ ] Second milestone
- [ ] Ship it

## Build Plan
1. Step one
2. Step two
3. Step three

## File Map
```
path/to/project/
├── main file
└── supporting files
```

## Uses Tools
- [[TOOL_name]] — what it does

## Key Decisions
- [[DEC_name]] — what was decided

## Related Projects
- [[01-Projects/related]] — how they connect

## Patterns Observed
- [[PAT_name]] — what pattern applies

---

## 🧭 CEIBA BREADCRUMBS
*Ceiba leaves notes here for future sessions. Read before touching this project.*

- **{TODAY}:** Created. No work done yet.

*Next action: Define first concrete task.*
"""


def template_tool(name, slug):
    clean_name = name.replace("TOOL_", "").replace("_", " ")
    return f"""---
title: "{name}"
type: tool
status: active
language: python
location: "tools/"
projects: []
tags: [tool, automation]
created: {TODAY}
---

# {clean_name}
**Type:** Tool / Script
**Language:** Python
**Location:** `tools/{slug.lower()}.py`

---

## What It Does
> One-paragraph description.

## Usage
```bash
python3 tools/{slug.lower()}.py [options]
```

### Options
| Flag | Description |
|------|-------------|
| `--help` | Show help |

## How It Works
1. Step one
2. Step two
3. Output

## Dependencies
- Python 3.x standard library

## Used By
- [[01-Projects/project_name]] — how it's used

## Related Tools
- [[TOOL_name]] — related tool

---

## 🧭 CEIBA BREADCRUMBS
- **{TODAY}:** Created.
"""


def template_decision(name, slug):
    clean_name = name.replace("DEC_", "").replace("_", " ")
    return f"""---
title: "{name}"
type: decision
status: active
date: {TODAY}
context: ""
alternatives: []
projects: []
tags: [decision]
created: {TODAY}
---

# Decision: {clean_name}
**Date:** {TODAY}
**Status:** ✅ Active

---

## Context
> What situation prompted this decision?

## Decision
> What was decided?

## Alternatives Considered
1. **Option A** — pros / cons
2. **Option B** — pros / cons
3. **Option C** — pros / cons

## Why This Choice
> Reasoning behind the decision.

## Consequences
- **Positive:** What this enables
- **Negative:** What this limits
- **Risks:** What could go wrong

## Related
- [[01-Projects/project]] — project this affects
- [[PAT_pattern]] — pattern this follows or breaks

---

## 🧭 CEIBA BREADCRUMBS
- **{TODAY}:** Decision recorded.
"""


def template_pattern(name, slug):
    clean_name = name.replace("PAT_", "").replace("_", " ")
    return f"""---
title: "{name}"
type: pattern
category: behavioral
frequency: occasional
severity: medium
first_seen: {TODAY}
projects: []
tags: [pattern, observation]
created: {TODAY}
---

# Pattern: {clean_name}
**Category:** Behavioral / Technical
**Frequency:** Occasional
**First Seen:** {TODAY}

---

## Description
> What is this pattern? When does it show up?

## Triggers
- What causes this pattern to activate?

## Signs
- How do you recognize it's happening?

## Impact
- What happens if left unchecked?

## Counter-Strategies
1. Strategy one
2. Strategy two

## Observations
| Date | Context | Notes |
|------|---------|-------|
| {TODAY} | First observed | Description |

## Related
- [[01-Projects/project]] — where this pattern appears
- [[DEC_decision]] — decisions influenced by this pattern

---

## 🧭 CEIBA BREADCRUMBS
- **{TODAY}:** Pattern documented.
"""


def template_design(name, slug):
    return f"""---
title: "{name}"
type: design
status: draft
version: "1.0"
projects: []
tags: [design, architecture]
created: {TODAY}
---

# {name}
**Status:** 📐 Draft
**Version:** 1.0
**Date:** {TODAY}

---

## Overview
> What system or component does this design describe?

## Goals
- Goal 1
- Goal 2

## Architecture
> High-level architecture description.

## Components
### Component A
- Responsibility:
- Interface:

### Component B
- Responsibility:
- Interface:

## Data Flow
```
Input → Process → Output
```

## Trade-offs
| Choice | Pros | Cons |
|--------|------|------|
| Approach A | Fast | Limited |
| Approach B | Flexible | Complex |

## Open Questions
- [ ] Question 1
- [ ] Question 2

## Related
- [[01-Projects/project]] — implements this design
- [[DEC_decision]] — key decisions

---

## 🧭 CEIBA BREADCRUMBS
- **{TODAY}:** Design drafted.
"""


def template_checkin(name, slug):
    return f"""---
title: "{name}"
type: check-in
date: {TODAY}
mood: ""
energy: ""
tags: [check-in, reflection]
created: {TODAY}
---

# Check-in — {TODAY}

## How are you actually doing?
> Honest answer here.

## Energy Level
> 1-10 scale. What's draining it? What's fueling it?

## What's Working
- Thing that's going well

## What's Not Working
- Thing that needs to change

## Wins This Week
- Win 1

## What's Being Avoided?
> Name it directly.

## Next Focus
> One thing for the next session.

---
"""


def template_knowledge(name, slug):
    clean_name = name.replace("_", " ")
    return f"""---
title: "{name}"
type: knowledge
status: active
category: ""
projects: []
tags: [knowledge]
created: {TODAY}
---

# {clean_name}

---

## What It Is
> One-paragraph description.

## Key Details
- Detail 1
- Detail 2

## How It Connects
- [[01-Projects/project]] — relationship
- [[05-Knowledge/tools/related]] — relationship

## Notes
- Notes here.

---

## 🧭 CEIBA BREADCRUMBS
- **{TODAY}:** Created.
"""


# Known names that override prefix-based type detection
KNOWN_TOOLS = {"vault_grapher", "session_tracker", "morning_briefing", "graph_query",
               "vault_healer", "ceiba_client", "memory_ingest", "prompt_guard",
               "vault_templates", "session_logger"}
KNOWN_PROJECTS = {"BehiqueBot", "eBay-Listing-Assistant", "Google-Trends-Scraper",
                  "Shopify-Store", "n8n-Agency", "AI-Ebook", "Telegram-Scraper-SaaS"}
# Meta-docs that should NOT get generic templates (they have custom structure)
META_DOCS = {"VAULT_INDEX", "primer", "observations", "IDEAS_BACKLOG", "context",
             "CLAUDE", "hub"}


TEMPLATES = {
    "project": template_project,
    "tool": template_tool,
    "decision": template_decision,
    "pattern": template_pattern,
    "design": template_design,
    "check-in": template_checkin,
    "knowledge": template_knowledge,
}


def create_file(file_type, name, dry_run=False):
    """Create a vault file from template."""
    if file_type not in TEMPLATES:
        print(f"❌ Unknown type: {file_type}")
        print(f"   Available: {', '.join(TEMPLATES.keys())}")
        return None

    # Clean up name for filename
    slug = name.replace(" ", "-").replace("/", "-")
    if not slug.endswith(".md"):
        filename = f"{slug}.md"
    else:
        filename = slug
        slug = slug[:-3]

    subdir = TYPE_DIRS.get(file_type, "05-Knowledge")
    dir_path = os.path.join(CEIBA, subdir)
    filepath = os.path.join(dir_path, filename)

    if os.path.exists(filepath):
        print(f"⚠️  Already exists: {filepath}")
        return filepath

    content = TEMPLATES[file_type](name, slug)

    if dry_run:
        print(f"Would create: {subdir}/{filename}")
        print(f"{'─' * 40}")
        print(content[:500] + "..." if len(content) > 500 else content)
        return filepath

    os.makedirs(dir_path, exist_ok=True)
    with open(filepath, "w") as f:
        f.write(content)

    print(f"✅ Created: {subdir}/{filename}")
    return filepath


def find_stub_files():
    """Find auto-generated stubs that need real templates."""
    stubs = []
    for root, dirs, files in os.walk(CEIBA):
        for f in files:
            if not f.endswith(".md"):
                continue
            path = os.path.join(root, f)
            try:
                with open(path) as fh:
                    content = fh.read(500)
                if "Auto-generated stub by vault_healer.py" in content:
                    name_no_ext = f[:-3]
                    # Skip meta-docs that have custom structure
                    if name_no_ext in META_DOCS:
                        continue
                    # Determine type from prefix first, then known names
                    if f.startswith("DEC_"):
                        file_type = "decision"
                    elif f.startswith("PAT_"):
                        file_type = "pattern"
                    elif f.startswith("TOOL_"):
                        file_type = "tool"
                    elif f.startswith("SYS_"):
                        file_type = "design"
                    elif f.startswith("SES_"):
                        file_type = "session"
                    elif name_no_ext in KNOWN_TOOLS:
                        file_type = "tool"
                    elif name_no_ext in KNOWN_PROJECTS:
                        file_type = "project"
                    else:
                        file_type = "knowledge"
                    stubs.append((path, name_no_ext, file_type))
            except Exception:
                pass
    return stubs


def apply_templates_to_stubs(dry_run=False):
    """Replace stub files with proper templates."""
    stubs = find_stub_files()
    if not stubs:
        print("✅ No stub files found — all vault files have content!")
        return 0

    print(f"\n  🔧 Found {len(stubs)} stub files to upgrade\n")
    upgraded = 0

    for path, name, file_type in stubs:
        if file_type not in TEMPLATES:
            print(f"  ⏭️  Skipping {name} (no template for type: {file_type})")
            continue

        slug = name.replace(" ", "-")
        content = TEMPLATES[file_type](name, slug)

        if dry_run:
            print(f"  Would upgrade: {name} ({file_type})")
            continue

        with open(path, "w") as f:
            f.write(content)
        upgraded += 1
        print(f"  ✅ Upgraded: {name} → {file_type} template")

    if not dry_run:
        print(f"\n  ✅ Upgraded {upgraded}/{len(stubs)} stub files")
    return upgraded


def list_templates():
    """Show all available templates."""
    print("\n  📋 Available Vault Templates\n")
    for name, func in TEMPLATES.items():
        subdir = TYPE_DIRS.get(name, "?")
        print(f"  • {name:12s} → Ceiba/{subdir}/")
    print(f"\n  Usage: python3 vault_templates.py <type> \"Name\"")
    print(f"  Stubs: python3 vault_templates.py --apply-missing")
    print()


def main():
    parser = argparse.ArgumentParser(description="Vault Template System")
    parser.add_argument("type", nargs="?", help="Template type (project, tool, decision, pattern, design, check-in)")
    parser.add_argument("name", nargs="?", help="Name for the new file")
    parser.add_argument("--list", action="store_true", help="Show available templates")
    parser.add_argument("--apply-missing", action="store_true", help="Upgrade stub files to proper templates")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    args = parser.parse_args()

    if args.list:
        list_templates()
        return

    if args.apply_missing:
        apply_templates_to_stubs(args.dry_run)
        return

    if not args.type or not args.name:
        parser.print_help()
        return

    create_file(args.type, args.name, args.dry_run)


if __name__ == "__main__":
    main()
