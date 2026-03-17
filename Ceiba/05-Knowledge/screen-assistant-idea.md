---
title: "screen-assistant-idea"
type: knowledge
tags: [idea:, real-time, screen]
created: 2026-03-16
---

# Idea: Real-Time Screen Assistant

**Captured:** 2026-03-14
**Status:** Idea — build later

---

## The Concept

A bot/system where Ceiba can see Kalani's screen in real time and assist on the fly. Use cases:
- Online labs, exams, assignments — "what's the answer to question 5?" → Ceiba replies instantly
- Cursor-following — Ceiba tracks where Kalani points and answers what's in front of him
- Verbal commands on the go — voice in, text/voice out, hands-free

## How It Could Work

- Screen capture feed → Ceiba reads it → responds to voice or text commands about what's on screen
- Claude in Chrome (already in the stack) is the closest existing tool — browser-level screen awareness
- For full desktop: would need a screen capture layer + voice input (Whisper already in BehiqueBot stack) + Ceiba as the brain
- Output: text reply, voice reply, or cursor overlay

## Why It Matters

This is the "Jarvis in the room" experience. Not reactive (you come to me) — I'm present while you work, available instantly, no context switching.

## Build Dependencies

- Screen capture or screenshot API
- Voice input (Whisper — already built in BehiqueBot)
- Fast response loop (low latency matters here)
- Claude in Chrome covers the browser case already

## Priority

Low right now — build after BehiqueBot → Notion, trends bot, and n8n agency are stable. But this is a real product eventually.
