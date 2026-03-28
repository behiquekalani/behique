# Project: behique

## Tech Stack
Python

## File Structure
```
├── _legacy/
│   ├── pending-notifications/
│   ├── ceiba_lite.py
│   ├── MIGRATE-TO-CODE.md
│   ├── notion-triage.jsx
│   ├── post-commit
│   ├── routing.py
│   └── setup_notion.py
├── bridge/
│   ├── cobo_instructions_2026-03-16.md
│   ├── COMPUTER2_MIND.md
│   ├── dispatch.sh
│   ├── README.md
│   ├── sleep.sh
│   ├── tasks.md
│   └── wake.sh
├── cache/
│   └── trends_cache.db
├── Ceiba/
│   ├── 00-Identity/
│   │   ├── Kalani.md
│   │   └── Psychologist-Framework.md
│   ├── 01-Projects/
│   │   ├── AI-Ebook.md
│   │   ├── Behique-Product.md
│   │   ├── BehiqueBot.md
│   │   ├── Book-to-Agent.md
│   │   ├── Colmena66-AI.md
│   │   ├── Computer-2.md
│   │   ├── Content-Funnel.md
│   │   ├── eBay-Listing-Assistant.md
│   │   ├── Google-Trends-Scraper.md
│   │   ├── MISSIONS.md
│   │   ├── n8n-Agency.md
│   │   ├── News-Intelligence-Bots.md
│   │   ├── Shopify-Store.md
│   │   ├── Spine-Architecture.md
│   │   └── Telegram-Scraper-SaaS.md
│   ├── 02-Goals/
│   │   ├── North-Star.md
│   │   └── Q3-2026.md
│   ├── 03-Check-ins/
│   │   ├── 2026-03-15.md
│   │   ├── 2026-03-16.md
│   │   ├── 2026-03-17.md
│   │   ├── 2026-03-18.md
│   │   ├── 2026-03-19.md
│   │   ├── template.md
│   │   └── weekly-2026-03-15.md
│   ├── 04-Patterns/
│   │   ├── decisions/
│   │   │   ├── DEC_Best_Not_Cheapest.md
│   │   │   ├── DEC_Claude_Code_HQ.md
│   │   │   ├── DEC_Ebay_Before_Shopify.md
│   │   │   ├── DEC_Event_Not_Schedule.md
│   │   │   ├── DEC_Model_Agnostic_Vault.md
│   │   │   ├── DEC_Ollama_First.md
│   │   │   └── DEC_Proxy_Rotation.md
│   │   ├── avoidance-pattern.md
│   │   ├── ceiba-design-system.md
│   │   ├── competitive_intel.md
│   │   ├── observations.md
│   │   ├── PAT_Avoidance_Revenue.md
│   │   ├── PAT_Event_Not_Schedule.md
│   │   └── PAT_Infrastructure_Creep.md
│   ├── 05-Knowledge/
│   │   ├── tools/
│   │   │   ├── TOOL_Agent_Kernel.md
│   │   │   ├── TOOL_BehiqueBot_Core.md
│   │   │   ├── TOOL_Ceiba_Lite.md
│   │   │   ├── TOOL_Dispatch.md
│   │   │   ├── TOOL_Listing_Pipeline.md
│   │   │   ├── TOOL_n8n.md
│   │   │   ├── TOOL_Notify_Relay.md
│   │   │   ├── TOOL_Trends_Scraper.md
│   │   │   └── TOOL_Vault_Grapher.md
│   │   ├── architecture-spine.md
│   │   ├── computer2-full-context.md
│   │   ├── computer2-openclaw-instructions.md
│   │   ├── computer2-session-instructions.md
│   │   ├── openclaw-setup.md
│   │   ├── primer.md
│   │   ├── screen-assistant-idea.md
│   │   ├── session_tracker.md
│   │   ├── session-2026-03-15-capture.md
│   │   ├── system-map-render.jsx
│   │   ├── system-map.jsx
│   │   ├── vault_grapher.md
│   │   └── VAULT_INDEX.md
│   ├── 05-Resources/
│   │   └── tool_database.md
│   ├── 06-Designs/
│   │   ├── agent-kernel-architecture.md
│   │   ├── ccp-cluster-architecture.md
│   │   ├── ccp-grpc-retry-manager.md
│   │   ├── ceiba-cobo-communication-protocol-ccp.md
│   │   ├── ceiba-cobo-grpc-prototype.md
│   │   ├── ceiba-memory-protocol-cmp.md
│   │   ├── SYS_AI_Cluster.md
│   │   ├── SYS_Bridge.md
│   │   └── SYS_Vault_Graph.md
│   ├── 06-Sessions/
│   │   ├── 2026-03-16-report.md
│   │   ├── 2026-03-16.json
│   │   ├── ingestion_log.json
│   │   ├── SES_2026_03_16_claude_code.md
│   │   └── SES_20260316.md
│   ├── 07-Tasks/
│   │   └── jellyfin-setup-cobo.md
│   ├── 07-Transcripts/
│   │   ├── 2026-03-17_Rick_Astley_-_Never_Gonna_Give_You_Up_(Official_Video)_(4K_Remaster).json
│   │   ├── 2026-03-17_Rick_Astley_-_Never_Gonna_Give_You_Up_(Official_Video)_(4K_Remaster).txt
│   │   ├── 2026-03-17_Video_by_copycats.digital.json
│   │   ├── 2026-03-17_Video_by_copycats.digital.txt
│   │   ├── 2026-03-18_Video_by_liamjohnston.ai.json
│   │   ├── 2026-03-18_Video_by_liamjohnston.ai.txt
│   │   ├── 2026-03-19_Video_by_liamjohnston.ai.json
│   │   ├── 2026-03-19_Video_by_liamjohnston.ai.txt
│   │   ├── COMP2_2026-03-16_vision_session.md
│   │   ├── README.md
│   │   └── TRANSCRIPT_2026-03-16_session_summary.md
│   ├── 08-Images/
│   │   ├── IMAGES_2026-03-16_quest-dashboard-inspo.md
│   │   ├── IMG_2026-03-16_focuslab_dashboard_ref.md
│   │   └── README.md
│   ├── backups/
│   │   ├── CLAUDE.md.backup.20260317
│   │   └── session8_handoff_20260317.md
│   ├── dashboards/
│   │   ├── behique-hub.html
│   │   ├── ceiba_dashboard.html
│   │   ├── ceiba-hq.html
│   │   ├── ceiba-synth.html
│   │   ├── command-hub.html
│   │   ├── hub.json
│   │   ├── quest-dashboard.html
│   │   ├── quests.json
│   │   └── unified-hub.html
│   ├── faces/
│   │   ├── api/
│   │   │   └── dashboard.json
│   │   └── dashboard.html
│   ├── transcripts/
│   │   └── session8_system_audit_20260317.md
│   ├── BEHIQUE_HUB_DESIGN_SPEC.md
│   ├── HOME.md
│   ├── IDEAS_BACKLOG.md
│   ├── vault_graph.json
│   ├── VAULT_GRAPH.md
│   └── VAULT_INDEX.md
├── dashboards/
│   ├── allocator-eval-review.html
│   ├── ceiba-eval-review.html
│   ├── ceiba-face.html
│   ├── professor-eval-review.html
│   └── quest-dashboard.html
├── modules/
│   ├── classifier.py
│   ├── ebay_command.py
│   ├── memory.py
│   ├── notion_handler.py
│   ├── routing.py
│   ├── transcribe_command.py
│   └── voice_handler.py
├── output/
│   ├── checkpoint-log.txt
│   ├── dashboard.html
│   ├── notify-agent-err.log
│   ├── notify-agent.log
│   ├── notify-log.txt
│   ├── scraper_log_2026-03-15.log
│   ├── scraper_log_2026-03-16.log
│   ├── scraper_log_2026-03-17.log
│   ├── scraper_log_2026-03-18.log
│   ├── scraper_log_2026-03-19.log
│   ├── top_picks_2026-03-15.txt
│   ├── top_picks_2026-03-17.txt
│   ├── top_picks_2026-03-18.txt
│   ├── top_picks_2026-03-19.txt
│   ├── trending_products_2026-03-15.csv
│   ├── trending_products_2026-03-15.json
│   ├── trending_products_2026-03-17.csv
│   ├── trending_products_2026-03-17.json
│   ├── trending_products_2026-03-18.csv
│   ├── trending_products_2026-03-18.json
│   ├── trending_products_2026-03-19.csv
│   └── trending_products_2026-03-19.json
├── product_research_engine/
│   ├── cache/
│   │   └── research.db
│   ├── cli/
│   │   └── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── feature_engineering.py
│   │   ├── models.py
│   │   ├── product_normalizer.py
│   │   ├── scoring_engine.py
│   │   ├── trends_adapter.py
│   │   └── utils.py
│   ├── ebay/
│   │   ├── __init__.py
│   │   ├── ebay_client.py
│   │   └── ebay_cross_reference.py
│   ├── output/
│   │   ├── engine.log
│   │   ├── products_2026-03-15.csv
│   │   ├── products_2026-03-15.json
│   │   └── top25_report_2026-03-15.txt
│   ├── pipeline/
│   │   ├── __init__.py
│   │   ├── cross_reference.py
│   │   ├── discovery.py
│   │   ├── reporting.py
│   │   └── scoring.py
│   ├── scrapers/
│   │   ├── __init__.py
│   │   ├── amazon_best_sellers.py
│   │   ├── base_scraper.py
│   │   ├── costco_popular.py
│   │   ├── home_depot_best_sellers.py
│   │   ├── target_trending.py
│   │   └── walmart_trending.py
│   ├── config.yaml
│   ├── main.py
│   ├── requirements.txt
│   └── seed_from_trends.py
├── skills/
│   ├── ceiba-accountability/
│   │   └── SKILL.md
│   ├── code-auditor/
│   │   └── SKILL.md
│   ├── idea-classifier/
│   │   └── SKILL.md
│   ├── kernel/
│   │   └── SKILL.md
│   ├── security-auditor/
│   │   └── SKILL.md
│   ├── session-closer/
│   │   └── SKILL.md
│   ├── session-tracker/
│   │   └── SKILL.md
│   ├── trends-scraper/
│   │   └── SKILL.md
│   ├── vault-architect/
│   │   └── SKILL.md
│   ├── ceiba.skill
│   ├── professor.skill
│   └── the-allocator.skill
├── templates/
│   └── skins/
│       ├── ceiba-face-wireframe.html
│       ├── pipboy-quest-log.html
│       └── README.md
├── tools/
│   ├── _archived/
│   │   ├── chatgpt_relay.py
│   │   ├── export_hub_data.py
│   │   ├── graph_query.py
│   │   ├── install-notify-agent.sh
│   │   ├── memory_ingest.py
│   │   ├── morning_briefing.py
│   │   ├── notify.py
│   │   ├── notion-triage.jsx
│   │   ├── session_logger.py
│   │   ├── session_tracker.py
│   │   ├── setup_notion.py
│   │   ├── vault_context_engine.py
│   │   ├── vault_grapher.py
│   │   ├── vault_healer.py
│   │   └── vault_templates.py
│   ├── _frozen/
│   │   ├── ai_agent_kernel/
│   │   │   ├── proto/
│   │   │   │   ...
│   │   │   ├── skills/
│   │   │   │   ...
│   │   │   ├── __init__.py
│   │   │   ├── ccp_pb2_grpc.py
│   │   │   ├── ccp_pb2.py
│   │   │   ├── ceiba_client.py
│   │   │   ├── cmp_log.jsonl
│   │   │   ├── cmp.db
│   │   │   ├── cmp.py
│   │   │   ├── cobo_server.py
│   │   │   ├── kernel_dispatcher.py
│   │   │   └── main.py
│   │   └── ai_cluster/
│   │       ├── kernel/
│   │       │   ...
│   │       ├── memory/
│   │       │   ...
│   │       ├── skills/
│   │       │   ...
│   │       ├── tasks/
│   │       │   ...
│   │       └── ARCHITECTURE.md
│   ├── ceiba-cli/
│   │   └── package.json
│   ├── ebay-listing-assistant/
│   │   ├── ai/
│   │   │   ├── __init__.py
│   │   │   └── content_generator.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── pipeline.py
│   │   │   ├── pricing.py
│   │   │   ├── shipping.py
│   │   │   ├── types_v1.py
│   │   │   └── types.py
│   │   ├── listings/
│   │   │   ├── funko_pop_the_godfather_vito_corleone_mi_20260316_155205.json
│   │   │   ├── funko_pop_the_godfather_vito_corleone_mi_20260316_155205.txt
│   │   │   ├── hello_kitty_strawberry_coffee_mug_cup_sa_20260316_155215.json
│   │   │   ├── hello_kitty_strawberry_coffee_mug_cup_sa_20260316_155215.txt
│   │   │   ├── hello_kitty_strawberry_coffee_mug_cup_sa_20260316_155231.json
│   │   │   └── hello_kitty_strawberry_coffee_mug_cup_sa_20260316_155231.txt
│   │   ├── media/
│   │   │   ├── __init__.py
│   │   │   └── image_handler.py
│   │   ├── providers/
│   │   │   ├── ebay/
│   │   │   │   ...
│   │   │   └── __init__.py
│   │   ├── research/
│   │   │   └── hello_kitty_mug_apify_research_20260317.md
│   │   ├── storage/
│   │   │   ├── __init__.py
│   │   │   └── history.py
│   │   ├── tests/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── quick_list.py
│   │   └── run.py
│   ├── n8n-workflows/
│   │   ├── n8n_mcp_test_20260317.md
│   │   └── spec-prompt-generator.json
│   ├── ceiba
│   ├── ceiba_audit.py
│   ├── ceiba_bridge.py
│   ├── ceiba_run.py
│   ├── ceiba_transcribe.py
│   ├── codegpt_bridge.py
│   ├── setup-ssh-remote.sh
│   ├── trends_scorer.py
│   └── trends_scraper.py
├── .env.example
├── CLAUDE.md
├── context.md
├── main.py
├── memory.sh
├── nixpacks.toml
├── primer.md
├── Procfile
├── project_memory.md
├── README.md
├── requirements.txt
└── vectors.db
```

## Key Files
- .env.example (46 bytes)

## README (first 20 lines)

