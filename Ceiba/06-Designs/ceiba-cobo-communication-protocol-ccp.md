---
title: "ceiba-cobo-communication-protocol-ccp"
type: design
tags: [ceiba–cobo, communication, protocol]

projects:
  - Computer-2
  - Spine-Architecture
systems:
  - SYS_Bridge
  - SYS_AI_Cluster
created: 2026-03-16
---

# Ceiba–Cobo Communication Protocol (CCP) Specification
**Source:** ChatGPT (2026-03-16)
**Status:** DESIGN — needs implementation
**Priority:** HIGH — enables autonomous cross-computer work

---

## 1. Overview

CCP enables Ceiba (controller/Mac) to trigger autonomous tasks on Cobo (executor/Linux) and receive updates, errors, and results reliably.

**Supports:**
- Bidirectional messaging
- Task lifecycle management
- Failure recovery & retries
- CMP hooks for memory logging
- Audit trail

---

## 2. Protocol Roles

| Role | Description |
|------|-------------|
| Ceiba | Task orchestrator — triggers tasks, monitors, collects results |
| Cobo | Task executor — runs tasks autonomously, reports progress/results |
| CMP (optional) | Cluster-wide logging, analytics, memory hooks |

---

## 3. Message Types

### Header (all messages)

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
| TASK_INIT | Ceiba → Cobo | Request to start a task |
| TASK_ACK | Cobo → Ceiba | Acknowledge receipt |
| TASK_STATUS | Cobo → Ceiba | Ongoing progress updates |
| TASK_RESULT | Cobo → Ceiba | Final output |
| TASK_ERROR | Cobo → Ceiba | Error reporting |
| RETRY_REQUEST | Ceiba → Cobo | Request task retry |
| HEARTBEAT | Both | Keep-alive / health check |

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

### Full TASK_INIT Example

```json
{
  "header": {
    "version": "1.0",
    "message_id": "abc-def-123",
    "timestamp": "2026-03-16T12:00:00Z",
    "source": "Ceiba",
    "destination": "Cobo"
  },
  "type": "TASK_INIT",
  "payload": {
    "task_id": "123e4567-e89b-12d3-a456-426614174000",
    "task_type": "image_classification",
    "parameters": {"image_url": "s3://bucket/img.png"},
    "timeout_ms": 5000,
    "priority": "high",
    "memory_hook": true
  }
}
```

---

## 5. Workflows

### 5.1 Task Execution Flow

```
Ceiba                        Cobo
  | TASK_INIT                |
  |------------------------->|
  |                          |
  |       TASK_ACK           |
  |<-------------------------|
  |                          |
  |       TASK_STATUS        |
  |<-------------------------|
  |       TASK_STATUS        |
  |<-------------------------|
  |       TASK_RESULT        |
  |<-------------------------|
```

### 5.2 Retry & Failure Handling

1. **Timeouts:** If TASK_ACK or TASK_RESULT not received within timeout_ms → RETRY_REQUEST
2. **Retries:** Cobo restarts task with incremented attempt counter
3. **Persistent failure:** After MAX_RETRIES → log to CMP, alert operator

### 5.3 Heartbeat (parallel)

```
Ceiba <---> Cobo: HEARTBEAT every 30s
```

---

## 6. CMP Integration Hooks

- `memory_hook: true` in task payload → Cobo logs execution state to CMP
- Ceiba forwards TASK_STATUS and TASK_RESULT to CMP endpoints
- Audit trail: every message stored with timestamp + message_id

---

## 7. Python Implementation

```python
import uuid, time, json
import requests

BASE_URL = "http://cobo.local/api"  # Or bridge.merchoo.shop:9876

def send_task(task_type, params, timeout_ms=5000, priority="medium", memory_hook=True):
    task_id = str(uuid.uuid4())
    message = {
        "header": {
            "version": "1.0",
            "message_id": str(uuid.uuid4()),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "source": "Ceiba",
            "destination": "Cobo"
        },
        "type": "TASK_INIT",
        "payload": {
            "task_id": task_id,
            "task_type": task_type,
            "parameters": params,
            "timeout_ms": timeout_ms,
            "priority": priority,
            "memory_hook": memory_hook
        }
    }

    response = requests.post(f"{BASE_URL}/task", json=message)
    if response.status_code != 200:
        raise Exception("Failed to send task")

    ack = response.json()
    if ack.get("type") != "TASK_ACK":
        raise Exception("Task not acknowledged")

    return task_id

def poll_task_result(task_id):
    for _ in range(10):
        res = requests.get(f"{BASE_URL}/task/{task_id}/status").json()
        if res["type"] == "TASK_RESULT":
            return res["payload"]
        elif res["type"] == "TASK_ERROR":
            print(f"Task error: {res['payload']}")
            return None
        time.sleep(1)
    print("Timeout: requesting retry")
    requests.post(f"{BASE_URL}/task/{task_id}/retry")
    return None

# Example usage
task_id = send_task("image_classification", {"image_url": "s3://bucket/img.png"})
result = poll_task_result(task_id)
print("Final result:", result)
```

---

## 8. Serialization & Versioning

- **Serialization:** Protobuf preferred for speed, JSON for debug/web
- **Versioning:** Semantic (MAJOR.MINOR.PATCH) in header
  - Backward compatible → increment MINOR
  - Breaking changes → increment MAJOR

---

## CEIBA NOTES

- **Existing bridge:** bridge.merchoo.shop:9876 with bearer auth — can extend this
- The bridge already handles HTTP POST with JSON — CCP messages can ride on top
- V1: HTTP REST (works now), V2: WebSocket for streaming status updates
- MAX_RETRIES = 3, timeout_ms = 5000 as defaults
- Memory hook writes to CMP storage (SQLite V1, vector DB V2)
- HEARTBEAT can use the bridge's existing ping endpoint
- The `task_type` field maps to Agent Kernel's SkillRegistry
- This protocol is the transport layer; Agent Kernel is the orchestration layer
