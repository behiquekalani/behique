# Distributed AI Agent Kernel Architecture
**Source:** ChatGPT (2026-03-16)
**Status:** DESIGN — needs implementation
**Priority:** HIGH — foundational infrastructure

---

## 1. Overview

Two-node split:

| Node | Role |
|------|------|
| Ceiba (Controller/Mac) | Task queue, scheduler, skill registry, memory interface |
| Cobo (Executor/Linux) | Worker spawning, task execution, result reporting |

Key capabilities:
- Task Queue & Prioritization: priority-based scheduling, dynamic insertion
- Worker Management: spawn, monitor, terminate safely
- Task Routing & Scheduling: assign by skill requirement
- Dynamic Skill Registry: register/update skills at runtime
- Memory Integration: query past results and agent knowledge

---

## 2. Module Structure

```
ai_agent_kernel/
├── controller/
│   ├── __init__.py
│   ├── task_queue.py
│   ├── scheduler.py
│   ├── skill_registry.py
│   ├── memory_interface.py
│   └── comms.py
├── executor/
│   ├── __init__.py
│   ├── worker.py
│   ├── worker_manager.py
│   ├── task_handler.py
│   └── comms.py
├── common/
│   ├── __init__.py
│   ├── data_models.py
│   ├── protocols.py
│   └── utils.py
└── main.py
```

---

## 3. Data Schemas

### 3.1 Task

```python
from enum import Enum
from pydantic import BaseModel
from typing import Any, Dict, Optional
import uuid
import time

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class TaskPriority(int, Enum):
    LOW = 1
    MEDIUM = 5
    HIGH = 10

class Task(BaseModel):
    id: str = str(uuid.uuid4())
    skill: str
    input_data: Dict[str, Any]
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    created_at: float = time.time()
    assigned_worker: Optional[str] = None
    result: Optional[Any] = None
```

### 3.2 Worker

```python
class WorkerStatus(str, Enum):
    IDLE = "idle"
    BUSY = "busy"
    OFFLINE = "offline"

class Worker(BaseModel):
    id: str
    hostname: str
    pid: int
    status: WorkerStatus = WorkerStatus.IDLE
    skills: list[str] = []
    last_heartbeat: float = time.time()
```

### 3.3 Skill Definition

```python
class Skill(BaseModel):
    name: str
    description: str
    version: str
    executor_module: str   # Python module to import dynamically
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
```

---

## 4. Task Queue & Scheduler

Priority queue using heapq (min-heap with negated priority):

```python
import heapq
from common.data_models import Task

class TaskQueue:
    def __init__(self):
        self._queue = []

    def push(self, task: Task):
        heapq.heappush(self._queue, (-task.priority, task.created_at, task))

    def pop(self) -> Task:
        if self._queue:
            return heapq.heappop(self._queue)[2]
        return None

    def peek(self):
        return self._queue[0][2] if self._queue else None
```

Scheduler:

```python
class Scheduler:
    def __init__(self, workers, task_queue):
        self.workers = workers
        self.task_queue = task_queue

    def assign_tasks(self):
        for worker in self.workers:
            if worker.status == "idle":
                task = self.task_queue.pop()
                if task:
                    task.assigned_worker = worker.id
                    worker.status = "busy"
                    print(f"Assigned {task.id} to {worker.id}")
```

---

## 5. Worker Process Management (Executor/Cobo)

```python
import multiprocessing
import time

def worker_process(task_queue, result_queue):
    while True:
        task = task_queue.get()
        if task is None:
            break
        result = execute_task(task)
        result_queue.put((task.id, result))

class WorkerManager:
    def __init__(self):
        self.workers = []

    def spawn_worker(self, n=1):
        for _ in range(n):
            p = multiprocessing.Process(
                target=worker_process,
                args=(task_queue, result_queue)
            )
            p.start()
            self.workers.append(p)
```

---

## 6. Skill Registry

```python
class SkillRegistry:
    def __init__(self):
        self.skills = {}

    def register_skill(self, skill: Skill):
        self.skills[skill.name] = skill

    def get_skill(self, name: str) -> Skill:
        return self.skills.get(name)
```

Dynamic execution:

```python
import importlib

def execute_task(task: Task):
    skill_module = importlib.import_module(task.skill)
    return skill_module.run(**task.input_data)
```

---

## 7. Memory Integration

```python
class MemoryInterface:
    def __init__(self, memory_db):
        self.db = memory_db  # Redis, SQLite, or vector DB

    def retrieve(self, query: str):
        return self.db.search(query)

    def store(self, task: Task):
        self.db.insert({"task_id": task.id, "result": task.result})
```

---

## 8. Communication Protocols

### Controller <-> Executor (TCP/WebSocket or gRPC)

Task assignment:
```json
{
    "type": "task_assign",
    "task": {
        "id": "uuid",
        "skill": "nlp_translate",
        "input_data": {"text": "Hello"}
    }
}
```

Result:
```json
{
    "type": "task_result",
    "task_id": "uuid",
    "status": "completed",
    "result": "Hola"
}
```

Heartbeat:
```json
{
    "type": "heartbeat",
    "worker_id": "abc123",
    "status": "idle"
}
```

---

## 9. System Diagram

```
         +--------------------+
         | Controller (Ceiba) |
         |--------------------|
         | TaskQueue           |
         | Scheduler           |
         | SkillRegistry       |
         | MemoryInterface     |
         +--------+-----------+
                  |
                  | Task Assignment / Results
                  v
         +--------------------+
         | Executor (Cobo)    |
         |--------------------|
         | WorkerManager       |
         | Workers (processes) |
         | TaskHandler         |
         +--------------------+
```

---

## 10. Scaling & Reliability Notes

- **Fault Tolerance:** Tasks re-queued if workers fail or heartbeat missed
- **Dynamic Skills:** Register at runtime; tasks can request specific versions
- **Memory Integration:** Query past results to avoid redundant computation
- **Cluster Extensibility:** Additional executors with minimal changes

---

## CEIBA NOTES

- This is ChatGPT's design doc. Ceiba implements.
- Bridge already exists at bridge.merchoo.shop:9876 — can reuse HTTP transport
- Pydantic models are clean — install with `pip install pydantic`
- Start with TaskQueue + Scheduler on Ceiba, WorkerManager on Cobo
- Memory can use SQLite initially, upgrade to vector DB later
- Next step: ChatGPT says "produce ~300 line prototype" — tell them YES
