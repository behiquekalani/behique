# Next Objective: Reactive Content Wiring

## Goal
Wire BIOS Intelligence to the Content Empire library to turn static posts into reactive weapons.

## Implementation Logic
1. **Input:** BIOS `bios/storage/signals.json` detects a trending topic (e.g., "AI Regulation").
2. **Matching:** Intelligence layer scans the 2000+ post library for relevant keywords.
3. **Scoring:** Assign a `relevance_score` to matched posts.
4. **Flagging:** Create a `bios/storage/reactive_queue.json` with the following schema:

```json
{
  "generated_at": "2026-03-23T10:00:00Z",
  "trending_topics": ["crypto", "geopolitics", "ai"],
  "queue": [
    {
      "post_id": "instagram-content-batch-5-security.md",
      "title": "5 AI Security Mistakes That Could Cost You Everything",
      "relevance_score": 0.92,
      "matched_topics": ["ai", "security"],
      "action": "PUBLISH_NOW",
      "target_platform": "instagram",
      "reason": "AI security trending with 71 mentions, negative sentiment"
    }
  ]
}
```

## Success Metric
The ability to move from "Signal Detected" to "Post Flagged for Upload" with zero manual searching.

## Dependencies
- BIOS perception layer (DONE)
- BIOS intelligence engine (DONE)
- Content library indexed and searchable (TODO)
- Platform accounts created (BLOCKED on Kalani)

## How to Start a Session for This Work
Say to Claude Code:
"Read PROJECT_STATUS.md and STRATEGY_REFERENCE.md. Build the reactive content wiring from ROADMAP_CONTENT_WIRING.md. Do not suggest new projects. Only focus on this connection."
