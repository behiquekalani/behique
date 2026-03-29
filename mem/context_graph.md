---
layer: L2-cache
purpose: Bidirectional map of all entities and their relationships
last_modified: 2026-03-28
node_count: 28
edge_count: 45
---

# Context Graph

nodes:

  # === PROJECTS ===
  - id: project-gumroad-store
    type: project
    status: active
    priority: 1
    description: "Behike Gumroad store - digital products for solopreneurs"
    links: [tool-claude-code, tool-gumroad, pattern-product-folder, pattern-gumroad-listing, person-kalani, product-bundles, project-content-empire]

  - id: project-ceiba-v2
    type: project
    status: active
    priority: 2
    description: "Memory architecture upgrade - Context Trio, Status Tracker, Knowledge Library, Fleet Sync"
    links: [tool-claude-code, tool-git, person-kalani]

  - id: project-instagram
    type: project
    status: todo
    priority: 3
    description: "@behikeai Instagram - 2000+ posts ready, needs posting"
    links: [project-gumroad-store, pattern-copywriting-voice]

  - id: project-youtube
    type: project
    status: todo
    priority: 4
    description: "YouTube channel - 2 scripts ready to record"
    links: [project-gumroad-store, pattern-copywriting-voice, person-kalani]

  - id: project-bios
    type: project
    status: backlog
    description: "BIOS Intelligence System - architecture done, Phase 0"
    links: [tool-claude-code]

  - id: project-behiquebot
    type: project
    status: active
    description: "Telegram bot live on Railway"
    links: [tool-railway, tool-telegram]

  - id: project-polymarket
    type: project
    status: backlog
    description: "Polymarket trading research - $500 ready"
    links: [person-kalani]

  - id: project-ai-agent-service
    type: project
    status: backlog
    description: "AI Agent Installation Service - landing page built"
    links: [project-gumroad-store]

  - id: project-lumina
    type: project
    status: active
    description: "Solfeggio frequency app - 528Hz, brown/pink noise"
    links: [tool-claude-code]

  - id: project-content-empire
    type: project
    status: todo
    description: "YouTube scripts, blog posts, content pipeline"
    links: [project-youtube, project-instagram, pattern-copywriting-voice]

  # === PRODUCTS (grouped) ===
  - id: product-blueprints
    type: product-group
    status: active
    count: 18
    description: "Business blueprints - fill-in PDF format, dark theme, 8 modules each"
    links: [project-gumroad-store, pattern-blueprint-css, pattern-cover-html, pattern-thumbnail-html]

  - id: product-tutorials
    type: product-group
    status: active
    count: 7
    description: "Tutorial guides - First Dollar, Gumroad AI, Offline AI, Social Media, Claude Code x3"
    links: [project-gumroad-store, pattern-blueprint-css, pattern-cover-html]

  - id: product-bundles
    type: product-group
    status: todo
    count: 2
    description: "Blueprint Bundle ($49), Voice Bible ($16.99)"
    links: [project-gumroad-store, product-blueprints]

  # === TOOLS ===
  - id: tool-claude-code
    type: tool
    description: "Primary build tool - terminal AI assistant"
    links: [person-kalani, project-gumroad-store, project-ceiba-v2]

  - id: tool-gumroad
    type: tool
    description: "Sales platform - behike.gumroad.com"
    links: [project-gumroad-store]

  - id: tool-git
    type: tool
    description: "Version control - SSH push to GitHub"
    links: [project-ceiba-v2, project-gumroad-store]

  - id: tool-brave
    type: tool
    description: "Browser for PDF rendering with --force-device-scale-factor=2"
    links: [pattern-cover-html, pattern-thumbnail-html]

  - id: tool-railway
    type: tool
    description: "Hosting for BehiqueBot"
    links: [project-behiquebot]

  - id: tool-telegram
    type: tool
    description: "Bot platform for BehiqueBot"
    links: [project-behiquebot]

  - id: tool-syncthing
    type: tool
    description: "File sync between Ceiba, Cobo, Naboria"
    links: [machine-ceiba, machine-cobo, machine-naboria]

  # === MACHINES ===
  - id: machine-ceiba
    type: machine
    description: "Primary Mac - claude-code, brave-pdf, git-push"
    links: [tool-claude-code, tool-brave, tool-git, person-kalani]

  - id: machine-cobo
    type: machine
    description: "Linux content gen - ollama, free-tier rotation"
    links: [tool-syncthing]

  - id: machine-naboria
    type: machine
    description: "Linux always-on - hosting, background tasks, discord bot"
    links: [tool-syncthing, project-behiquebot]

  # === PATTERNS ===
  - id: pattern-blueprint-css
    type: pattern
    file: "mem/patterns/blueprint-css.md"
    links: [product-blueprints, product-tutorials]

  - id: pattern-cover-html
    type: pattern
    file: "mem/patterns/cover-html.md"
    links: [product-blueprints, product-tutorials, tool-brave]

  - id: pattern-thumbnail-html
    type: pattern
    file: "mem/patterns/thumbnail-html.md"
    links: [product-blueprints, product-tutorials, tool-brave]

  - id: pattern-product-folder
    type: pattern
    file: "mem/patterns/product-folder.md"
    links: [project-gumroad-store]

  - id: pattern-copywriting-voice
    type: pattern
    file: "mem/patterns/copywriting-voice.md"
    links: [project-gumroad-store, project-instagram, project-youtube]

  - id: pattern-gumroad-listing
    type: pattern
    file: "mem/patterns/gumroad-listing.md"
    links: [project-gumroad-store, tool-gumroad]

  # === PEOPLE ===
  - id: person-kalani
    type: person
    role: founder
    description: "Kalani Andre Gomez Padin - builder, ADHD, INFJ, PR"
    links: [project-gumroad-store, project-ceiba-v2, machine-ceiba, tool-claude-code, project-bios, project-polymarket, project-ai-agent-service, project-lumina]
