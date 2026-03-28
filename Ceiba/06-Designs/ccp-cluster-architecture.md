---
title: "ccp-cluster-architecture"
type: design
tags: [ceiba/cobo, cluster, architecture, source:, code]

projects:
  - Computer-2
  - Spine-Architecture
systems:
  - SYS_AI_Cluster
  - SYS_Bridge
created: 2026-03-16
---

# Ceiba/Cobo Cluster Architecture
# Source: Code GPT output, 2026-03-16
# Status: DESIGN — reference document

---

## Architecture Diagram

```
+----------------+          gRPC Stream          +----------------+
|                |<----------------------------->|                |
|     Ceiba      |                               |      Cobo      |
| (Controller)   |                               |  (Executor)    |
|----------------|                               |----------------|
| - Task Manager |                               | - Task Runner  |
| - Retry Logic  |                               | - Retry Handler|
| - CMP Hooks    |                               | - CMP Hooks    |
| - Memory Log   |                               | - Memory Log   |
+----------------+                               +----------------+
          |                                               |
          |             Optional CMP Integration          |
          |---------------------------------------------->|
```

---

## Components

### Ceiba (Controller)
- Sends tasks (TASK_INIT)
- Receives updates (TASK_STATUS, TASK_RESULT, TASK_ERROR)
- Handles retry logic with exponential backoff
- Logs to CMP / memory

### Cobo (Executor)
- Executes tasks autonomously
- Streams progress updates
- Accepts RetryRequest
- Sends final result or error
- Hooks for memory logging

### CMP (Optional)
- Analytics & logging platform
- Receives task updates via memory_hook messages
- Enables cluster-wide auditing

---

## Timing Diagram with Retries & CMP Logging

```
Time -->

Ceiba                                Cobo                         CMP
  |                                   |                            |
  |---- TASK_INIT ------------------->|                            |
  |                                   |                            |
  |<--- TASK_STATUS(progress 0%) -----|                            |
  |<--- TASK_STATUS(progress 20%) ----|                            |
  |<--- TASK_STATUS(progress 40%) ----|                            |
  |                                   |                            |
  |<--- TASK_ERROR -------------------|                            |
  |                                   |                            |
  | log_to_cmp(Failed)               ->|                            |
  |                                   |                            |
  |--- RETRY_REQUEST (attempt=1) ---->|                            |
  |                                   |                            |
  |<--- TASK_STATUS(progress 0%) -----|                            |
  |<--- TASK_STATUS(progress 20%) ----|                            |
  |<--- TASK_STATUS(progress 40%) ----|                            |
  |<--- TASK_STATUS(progress 60%) ----|                            |
  |<--- TASK_STATUS(progress 80%) ----|                            |
  |<--- TASK_RESULT ------------------|                            |
  |                                   |                            |
  | log_to_cmp(Completed)           ->|                            |
```

---

## Task Lifecycle Summary

| Stage | Ceiba Action | Cobo Action | CMP/Mem Logging |
|-------|-------------|-------------|-----------------|
| Task Submission | Send TASK_INIT | Receive & ACK | Optionally log submission |
| Task Execution | Monitor streaming TASK_STATUS | Update progress incrementally | Log progress |
| Task Error | Receive TASK_ERROR | Identify failure | Log error |
| Retry Handling | Send RetryRequest with incremented attempt | Re-run task | Log retry event |
| Task Completion | Receive TASK_RESULT | Finalize task | Log completion |
| Max Retry Exceeded | Abort, mark task failed | Stop retrying | Log failure permanently |

---

## Production Notes

### Scaling
- Multiple Cobo executors can connect to Ceiba via a load balancer
- Ceiba can manage multiple task streams simultaneously

### Resilience
- Heartbeat messages (optional) for node health monitoring
- Automatic retry with backoff ensures high task completion rates

### CMP/Mem Integration
- All critical events (FAILED, COMPLETED, Retry) are logged
- Memory hook ensures task execution states are captured for analytics

### Extensibility
- Add new task types easily
- Protocol versioning ensures backward compatibility (Header.version)

---

## Files

| File | Purpose |
|------|---------|
| `tools/ai_agent_kernel/proto/ccp.proto` | Protobuf schema |
| `tools/ai_agent_kernel/ceiba_client.py` | Ceiba client with retry + CMP |
| `tools/ai_agent_kernel/cobo_server.py` | Cobo server with retry + CMP |
| `Ceiba/06-Designs/ccp-grpc-retry-manager.md` | Protocol spec (V1) |
| `Ceiba/06-Designs/ccp-cluster-architecture.md` | This file |
