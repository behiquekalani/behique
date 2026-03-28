---
title: "ccp-grpc-retry-manager"
type: design
tags: [ceiba-cobo, communication, protocol, source:, code]

projects:
  - Computer-2
systems:
  - SYS_Bridge
created: 2026-03-16
---

# Ceiba-Cobo Communication Protocol (CCP) — gRPC Streaming + Retry Manager
# Source: Code GPT output, 2026-03-16
# Status: DESIGN — not yet implemented

---

## 1. Overview

The Ceiba-Cobo Protocol (CCP) enables the Ceiba controller to trigger tasks on the Cobo executor and receive updates, errors, and results reliably. It supports:

- Bidirectional messaging
- Task lifecycle management
- Failure recovery & retries with exponential backoff
- CMP (Ceiba Memory Protocol) hooks
- Memory and audit logging

---

## 2. Protocol Roles

| Role | Description |
|------|-------------|
| Ceiba | Task orchestrator; triggers tasks, monitors execution, collects results |
| Cobo | Task executor; runs tasks autonomously, reports progress and results |
| CMP (optional) | Integrates with Ceiba for cluster-wide logging, analytics, and memory hooks |

---

## 3. Message Types

All messages include a header and payload.

### Header Fields

```json
{
  "version": "1.0",
  "message_id": "<UUID>",
  "timestamp": "<ISO8601 UTC>",
  "source": "Ceiba|Cobo",
  "destination": "Ceiba|Cobo"
}
```

### Message Types

| Type | Direction | Description |
|------|-----------|-------------|
| TASK_INIT | Ceiba -> Cobo | Request Cobo to start a task |
| TASK_ACK | Cobo -> Ceiba | Acknowledge receipt of task |
| TASK_STATUS | Cobo -> Ceiba | Ongoing task updates (0-100 progress) |
| TASK_RESULT | Cobo -> Ceiba | Final task output |
| TASK_ERROR | Cobo -> Ceiba | Error reporting |
| RETRY_REQUEST | Ceiba -> Cobo | Request task retry |
| HEARTBEAT | Both | Keep-alive and health check |

---

## 4. Task Schema

```json
{
  "task_id": "<UUID>",
  "task_type": "<string>",
  "parameters": { "...": "..." },
  "timeout_ms": 5000,
  "priority": "low|medium|high",
  "memory_hook": true
}
```

---

## 5. Workflows

### 5.1 Task Execution

```
Ceiba          Cobo
  | TASK_INIT       |
  |---------------->|
  |                 |
  |     TASK_ACK    |
  |<----------------|
  |                 |
  | <--- TASK_STATUS (progress updates)
  |                 |
  | <--- TASK_RESULT | or TASK_ERROR
```

### 5.2 Retry & Failure Handling

1. **Timeouts:** If TASK_ACK or TASK_RESULT not received within `timeout_ms`, Ceiba triggers RETRY_REQUEST.
2. **Retries:** Cobo restarts task with incremented attempt counter.
3. **Exponential backoff:** `BASE_BACKOFF * BACKOFF_FACTOR^(attempt-1)` between retries.
4. **Persistent failure:** After `MAX_RETRIES` (default 3), Ceiba logs to CMP and alerts operators.

---

## 6. CMP Integration Hooks

- `memory_hook: true` in task payload triggers Cobo to log execution state
- Ceiba forwards TASK_STATUS and TASK_RESULT to CMP endpoints
- All retries and failures logged with full context

---

## 7. Serialization & Versioning

- **Serialization:** Protobuf for speed + binary efficiency. JSON fallback for debug/web.
- **Versioning:** Semantic (MAJOR.MINOR.PATCH) in header `version` field.
  - Backward compatible changes -> increment MINOR
  - Breaking changes -> increment MAJOR

---

## 8. Transport

- **gRPC bidirectional streaming** for production (full duplex, retries on same channel)
- **HTTP/REST** fallback for simple use cases
- **TLS required** for production deployments

---

## 9. Production Recommendations

- Use TLS for gRPC channels
- Extend CMP logging to persist to a database or monitoring system
- Monitor heartbeat messages to detect dead Cobo nodes
- Consider task queue sharding for large clusters
- Use Protobuf schema versioning in Header.version for backward compatibility

---

## 10. Files

- Proto schema: `tools/ai_agent_kernel/proto/ccp.proto`
- Ceiba client (with retry + CMP): `tools/ai_agent_kernel/ceiba_client.py`
- Cobo server: `tools/ai_agent_kernel/cobo_server.py`
