---
title: "ceiba-memory-protocol-cmp"
type: design
tags: [ceiba, memory, protocol]

projects:
  - Spine-Architecture
systems:
  - SYS_AI_Cluster
created: 2026-03-16
---

# Ceiba Memory Protocol (CMP) Specification
**Source:** ChatGPT (2026-03-16)
**Status:** DESIGN — needs implementation
**Priority:** HIGH — foundational protocol for multi-agent memory

---

## 1. Overview

CMP defines a structured system for AI agents to store, retrieve, and manage memories safely.

**Guarantees:**
- Typed payloads for consistency
- Data integrity via validation
- Conflict detection and resolution for concurrent writes
- Semantic and keyword-based queries
- Role-based access control

**Agent Roles:**
- **Writer Agents:** Create/update memory entries
- **Reader Agents:** Query memory entries
- **Resolver Agents:** Handle conflicts and validation errors

**Core Principles:**
- Typed and versioned payloads
- Explicit permissions
- Deterministic conflict resolution

---

## 2. Memory Payload Types

| Type | Description |
|------|-------------|
| event | Specific occurrence or observation |
| action | Executed or planned action |
| metadata | Contextual/structural info about other memories |
| state | Snapshot of agent or system state |

### Memory Entry Schema

```json
{
  "id": "uuid-v4",
  "type": "event|action|metadata|state",
  "timestamp": "ISO8601",
  "payload": { "key": "value" },
  "tags": ["optional", "keywords"],
  "author": "agent_id",
  "version": 1,
  "permissions": {
    "read": ["agent_id1", "agent_id2"],
    "write": ["agent_id1"]
  },
  "hash": "sha256(payload + timestamp + author + version)"
}
```

Notes:
- `hash` ensures integrity
- `version` incremented on updates
- `tags` allow keyword search
- `permissions` control agent access

---

## 3. Validation Rules

- **Required Fields:** id, type, timestamp, payload, author, version, hash
- **Type Enforcement:** Must match allowed types
- **Payload Validation:** Schema-specific per type
- **Integrity Check:** hash must match SHA256(payload+timestamp+author+version)
- **Versioning:** New entries must increment version

---

## 4. Conflict Detection & Resolution

### Detection
- On write: compare incoming version with latest stored version
- If version equal → conflict detected

### Resolution Strategies
1. **Last-Write-Wins (LWW)** — newest timestamp overwrites
2. **Merge Payload** — combine non-conflicting fields
3. **Manual Resolver** — flag for Resolver Agent intervention

### Conflict Schema

```json
{
  "id": "uuid-v4",
  "type": "conflict",
  "conflicting_versions": [
    { "version": 2, "payload": {...}, "author": "agentA" },
    { "version": 2, "payload": {...}, "author": "agentB" }
  ],
  "resolved_by": "resolver_agent_id",
  "resolution_strategy": "merge|LWW|manual",
  "timestamp": "ISO8601"
}
```

---

## 5. Retrieval Queries

### 5.1 Keyword Search

```json
{
  "query_type": "keyword",
  "keywords": ["meeting", "budget"],
  "types": ["event", "metadata"],
  "time_range": {
    "from": "2026-01-01T00:00:00Z",
    "to": "2026-01-15T23:59:59Z"
  }
}
```

### 5.2 Semantic Search

```json
{
  "query_type": "semantic",
  "embedding": [0.12, 0.34, ...],
  "similarity_threshold": 0.85,
  "types": ["action"]
}
```

### Response Format

```json
{
  "results": [
    {
      "id": "uuid-v4",
      "type": "event",
      "payload": {...},
      "similarity_score": 0.92
    }
  ]
}
```

---

## 6. Access Control

- **Roles:** writer, reader, resolver
- **Per-entry permissions:** Defined in `permissions` field
- **Validation on access:** Check agent ID against permissions.read/write

---

## 7. Sequence Diagrams

### 7.1 Memory Write
```
Writer Agent -> CMP Storage: write(memory_entry)
CMP Storage -> CMP Storage: validate_entry()
CMP Storage --> Writer Agent: ack|conflict
```

### 7.2 Memory Read
```
Reader Agent -> CMP Storage: query(query_payload)
CMP Storage -> CMP Storage: check_permissions()
CMP Storage --> Reader Agent: results
```

### 7.3 Conflict Resolution
```
CMP Storage -> Resolver Agent: conflict_detected(conflict_payload)
Resolver Agent -> CMP Storage: resolution(resolved_payload)
CMP Storage -> CMP Storage: update_entry()
CMP Storage --> Writer Agents: update_notification
```

---

## 8. Example Payloads

### 8.1 Writing an Event

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "type": "event",
  "timestamp": "2026-03-16T12:00:00Z",
  "payload": {
    "description": "Team meeting completed",
    "participants": ["agentA", "agentB"]
  },
  "tags": ["meeting", "team"],
  "author": "agentA",
  "version": 1,
  "permissions": { "read": ["agentA","agentB"], "write": ["agentA"] },
  "hash": "sha256hashvalue"
}
```

### 8.2 Keyword Query

```json
{
  "query_type": "keyword",
  "keywords": ["meeting"],
  "types": ["event"]
}
```

### 8.3 Conflict Resolution

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "type": "conflict",
  "conflicting_versions": [
    { "version": 2, "payload": {"description":"Team meeting rescheduled"}, "author": "agentA" },
    { "version": 2, "payload": {"description":"Team meeting notes added"}, "author": "agentB" }
  ],
  "resolved_by": "resolverAgentC",
  "resolution_strategy": "merge",
  "timestamp": "2026-03-16T12:10:00Z"
}
```

---

## 9. Python Interface Sketches

```python
from typing import List, Dict, Any
from abc import ABC, abstractmethod

class MemoryEntry:
    def __init__(self, id: str, type: str, timestamp: str, payload: Dict[str, Any],
                  author: str, version: int, permissions: Dict[str, List[str]], tags: List[str] = []):
        self.id = id
        self.type = type
        self.timestamp = timestamp
        self.payload = payload
        self.author = author
        self.version = version
        self.permissions = permissions
        self.tags = tags
        self.hash = self.compute_hash()

    def compute_hash(self) -> str:
        import hashlib, json
        content = json.dumps(self.payload, sort_keys=True) + self.timestamp + self.author + str(self.version)
        return hashlib.sha256(content.encode()).hexdigest()

class CMPAgent(ABC):
    def __init__(self, agent_id: str):
        self.agent_id = agent_id

    @abstractmethod
    def write_memory(self, entry: MemoryEntry) -> bool:
        pass

    @abstractmethod
    def read_memory(self, query: Dict[str, Any]) -> List[MemoryEntry]:
        pass

    @abstractmethod
    def resolve_conflict(self, conflict_payload: Dict[str, Any]) -> MemoryEntry:
        pass
```

---

## CEIBA NOTES

- Start with SQLite backend, upgrade to vector DB (chromadb or qdrant) for semantic search
- The `hash` field is critical — prevents corrupted writes
- LWW is good enough for V1, merge for V2
- Tags are the MVP search — semantic search needs embeddings pipeline first
- Access control can be simple dict check for V1, upgrade to JWT or similar later
- This protocol integrates with the Agent Kernel's MemoryInterface
- ChatGPT produced a system overview diagram (2026-03-16) — shared in chat, shows Writer/Reader/Resolver agents, CMP Storage, conflict resolution flow, keyword/semantic search paths, access control roles
