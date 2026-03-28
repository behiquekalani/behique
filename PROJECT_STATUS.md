# BIOS Project Status & Architecture

## Core Identity
BIOS is a "Trend Capture & Income Engine" designed to convert raw data into automated revenue.

## Existing Infrastructure (DO NOT REBUILD)
1. **Perception Layer (Trend Capture Machine):** Ingests signals (crypto, social, markets) into `bios/storage/signals.json`.
2. **Intelligence Layer (Data-to-Decision Engine):** Processes signals into `bios/storage/insights.json`.
3. **Processing Layer (The Fleet):** 3 machines (Ceiba, Cobo, Naboria). Scheduler at `bios/scheduler/scheduler.py`.
4. **Arbitrage Engine (Polymarket Bot):** `tools/polymarket_telegram_bot.py` + `bios/ingestion/polymarket_fetcher.py`.
5. **Output Layer (Content Empire):** 2000+ dormant posts at `Ceiba/projects/content-empire/`.
6. **Product Library:** 60+ PDFs in `READY-TO-SELL/`. Landing pages at `themes/behike-store/landing-pages/`.
7. **Dashboard:** BIOS dashboard at port 8092. VR war room skeleton built.
8. **Daily Reports:** `bios/scheduler/daily_report.py` generates intelligence briefs.

## The Bottleneck
* **Account Infrastructure:** Instagram, YouTube, Gumroad, Polymarket accounts NOT yet live.
* **The "Connection Gap":** Intelligence Layer is not yet triggering the Output Layer.
* **Revenue = $0** because nothing is listed or posted.

## Operational Rules
* **DO NOT run /build autonomously.** Kalani controls when building happens.
* **DO NOT propose new products.** Focus on activating and wiring existing layers.
* **DO NOT rebuild existing tools.** Check what exists first.
* **Ask Kalani before starting work.** If he's not present, do nothing.
