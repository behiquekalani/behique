#!/usr/bin/env python3
"""
Distributed AI Agent Kernel — Full Prototype
Source: Code GPT (2026-03-16)
Status: PROTOTYPE — needs real networking + skill modules

Architecture:
  Controller (Ceiba/Mac): TaskQueue, Scheduler, SkillRegistry, MemoryInterface
  Executor (Cobo/Linux): WorkerManager, Workers, TaskHandler

Usage:
  python3 main.py  (runs demo with sample tasks)
"""

import multiprocessing
import importlib
import time
import uuid
import heapq
import json
from enum import Enum
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field


# ==================== DATA MODELS ====================

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskPriority(int, Enum):
    LOW = 1
    MEDIUM = 5
    HIGH = 10


class WorkerStatus(str, Enum):
    IDLE = "idle"
    BUSY = "busy"
    OFFLINE = "offline"


@dataclass
class Task:
    skill: str
    input_data: Dict[str, Any]
    priority: int = TaskPriority.MEDIUM
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    status: TaskStatus = TaskStatus.PENDING
    created_at: float = field(default_factory=time.time)
    assigned_worker: Optional[str] = None
    result: Optional[Any] = None

    def __lt__(self, other):
        """For heapq comparison — higher priority first, then earlier creation."""
        if self.priority != other.priority:
            return self.priority > other.priority  # Higher = first
        return self.created_at < other.created_at


@dataclass
class Worker:
    id: str
    hostname: str
    pid: int
    status: WorkerStatus = WorkerStatus.IDLE
    skills: List[str] = field(default_factory=list)
    last_heartbeat: float = field(default_factory=time.time)


@dataclass
class Skill:
    name: str
    description: str
    version: str
    executor_module: str
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)


# ==================== CONTROLLER: TASK QUEUE ====================

class TaskQueue:
    """Priority queue for tasks. Higher priority = processed first."""

    def __init__(self):
        self._queue: List[Task] = []

    def push(self, task: Task):
        heapq.heappush(self._queue, task)
        print(f"  [TaskQueue] Added: {task.id} (skill={task.skill}, priority={task.priority})")

    def pop(self) -> Optional[Task]:
        if self._queue:
            return heapq.heappop(self._queue)
        return None

    def peek(self) -> Optional[Task]:
        return self._queue[0] if self._queue else None

    def size(self) -> int:
        return len(self._queue)

    def is_empty(self) -> bool:
        return len(self._queue) == 0


# ==================== CONTROLLER: SKILL REGISTRY ====================

class SkillRegistry:
    """Dynamic skill registry — register and lookup skills at runtime."""

    def __init__(self):
        self.skills: Dict[str, Skill] = {}

    def register_skill(self, skill: Skill):
        self.skills[skill.name] = skill
        print(f"  [SkillRegistry] Registered: {skill.name} v{skill.version}")

    def get_skill(self, name: str) -> Optional[Skill]:
        return self.skills.get(name)

    def list_skills(self) -> List[str]:
        return list(self.skills.keys())

    def has_skill(self, name: str) -> bool:
        return name in self.skills


# ==================== CONTROLLER: MEMORY INTERFACE ====================

class MemoryInterface:
    """Simple in-memory store for task results. V2: SQLite/vector DB via CMP."""

    def __init__(self):
        self.store: List[Dict[str, Any]] = []

    def store_result(self, task: Task):
        entry = {
            "task_id": task.id,
            "skill": task.skill,
            "status": task.status.value,
            "result": task.result,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        self.store.append(entry)
        print(f"  [Memory] Stored result for task {task.id}")

    def retrieve(self, query: str) -> List[Dict]:
        """Simple keyword search across stored results."""
        results = []
        for entry in self.store:
            if query.lower() in json.dumps(entry).lower():
                results.append(entry)
        return results

    def dump(self) -> List[Dict]:
        return self.store


# ==================== CONTROLLER: SCHEDULER ====================

class Scheduler:
    """Assigns tasks from queue to idle workers."""

    def __init__(self, workers: Dict[str, Worker], task_queue: TaskQueue):
        self.workers = workers
        self.task_queue = task_queue

    def assign_tasks(self) -> List[Task]:
        """Assign pending tasks to idle workers. Returns list of assigned tasks."""
        assigned = []
        for worker in self.workers.values():
            if worker.status == WorkerStatus.IDLE:
                task = self.task_queue.pop()
                if task:
                    task.assigned_worker = worker.id
                    task.status = TaskStatus.RUNNING
                    worker.status = WorkerStatus.BUSY
                    assigned.append(task)
                    print(f"  [Scheduler] Assigned task {task.id} → worker {worker.id}")
        return assigned


# ==================== EXECUTOR: TASK EXECUTION ====================

def execute_task(task: Task) -> Task:
    """Execute a task by dynamically loading the skill module."""
    try:
        skill_module = importlib.import_module(task.skill)
        result = skill_module.run(**task.input_data)
        task.status = TaskStatus.COMPLETED
        task.result = result
    except ModuleNotFoundError:
        # Fallback: run built-in demo handler
        task.status = TaskStatus.COMPLETED
        task.result = f"[demo] Processed '{task.input_data}' with skill '{task.skill}'"
    except Exception as e:
        task.status = TaskStatus.FAILED
        task.result = f"Error: {str(e)}"
    return task


def worker_process(task_queue: multiprocessing.Queue, result_queue: multiprocessing.Queue, worker_id: str):
    """Worker process target — pulls tasks from queue, executes, pushes results."""
    while True:
        task = task_queue.get()
        if task is None:  # Poison pill
            break
        print(f"  [Worker {worker_id}] Executing task {task.id} (skill={task.skill})")
        completed = execute_task(task)
        result_queue.put(completed)
        print(f"  [Worker {worker_id}] Done: {task.id} → {task.status.value}")


# ==================== EXECUTOR: WORKER MANAGER ====================

class WorkerManager:
    """Manages worker processes on the executor node."""

    def __init__(self):
        self.workers: Dict[str, multiprocessing.Process] = {}
        self.task_queues: Dict[str, multiprocessing.Queue] = {}

    def spawn_worker(self, worker_id: str, result_queue: multiprocessing.Queue) -> multiprocessing.Queue:
        """Spawn a worker process. Returns its task queue for sending work."""
        task_q = multiprocessing.Queue()
        p = multiprocessing.Process(target=worker_process, args=(task_q, result_queue, worker_id))
        p.start()
        self.workers[worker_id] = p
        self.task_queues[worker_id] = task_q
        print(f"  [WorkerManager] Spawned worker {worker_id} (pid={p.pid})")
        return task_q

    def send_task(self, worker_id: str, task: Task):
        """Send a task to a specific worker."""
        if worker_id in self.task_queues:
            self.task_queues[worker_id].put(task)

    def shutdown_all(self):
        """Send poison pills and join all workers."""
        for wid, q in self.task_queues.items():
            q.put(None)
        for wid, p in self.workers.items():
            p.join(timeout=5)
            if p.is_alive():
                p.terminate()
            print(f"  [WorkerManager] Worker {wid} shut down")


# ==================== MAIN: DEMO RUN LOOP ====================

def main():
    print("=" * 60)
    print("  Behique Agent Kernel — Prototype v0.1")
    print("  Controller: Ceiba (Mac) | Executor: Local Demo")
    print("=" * 60)
    print()

    # --- Controller setup ---
    task_queue = TaskQueue()
    skill_registry = SkillRegistry()
    memory = MemoryInterface()

    # Register skills (demo — no actual module needed)
    skill_registry.register_skill(Skill(
        name="skills.sample_skill",
        description="Sample text processing skill",
        version="1.0",
        executor_module="skills.sample_skill"
    ))
    skill_registry.register_skill(Skill(
        name="skills.ebay_research",
        description="eBay sold listing research",
        version="0.1",
        executor_module="skills.ebay_research"
    ))

    print()

    # --- Add tasks ---
    task_queue.push(Task(
        skill="skills.sample_skill",
        input_data={"text": "Hello World"},
        priority=TaskPriority.HIGH
    ))
    task_queue.push(Task(
        skill="skills.sample_skill",
        input_data={"text": "Process this data"},
        priority=TaskPriority.MEDIUM
    ))
    task_queue.push(Task(
        skill="skills.ebay_research",
        input_data={"query": "Hello Kitty Mug", "condition": "Used"},
        priority=TaskPriority.HIGH
    ))
    task_queue.push(Task(
        skill="skills.sample_skill",
        input_data={"text": "Low priority task"},
        priority=TaskPriority.LOW
    ))

    print(f"\n  Queue size: {task_queue.size()} tasks\n")

    # --- Executor setup ---
    result_queue = multiprocessing.Queue()
    wm = WorkerManager()
    worker_ids = ["worker-alpha", "worker-beta"]

    print("--- Spawning workers ---")
    for wid in worker_ids:
        wm.spawn_worker(wid, result_queue)

    # --- Controller workers registry ---
    controller_workers = {}
    for wid in worker_ids:
        controller_workers[wid] = Worker(
            id=wid,
            hostname="localhost",
            pid=wm.workers[wid].pid,
            skills=["skills.sample_skill", "skills.ebay_research"]
        )

    scheduler = Scheduler(controller_workers, task_queue)

    print("\n--- Running task loop ---\n")

    # Simple run loop
    max_iterations = 20
    iteration = 0

    while iteration < max_iterations:
        iteration += 1

        # Assign tasks to idle workers
        assigned = scheduler.assign_tasks()

        # Send assigned tasks to worker processes
        for task in assigned:
            wm.send_task(task.assigned_worker, task)

        # Collect results
        while not result_queue.empty():
            completed_task = result_queue.get_nowait()
            memory.store_result(completed_task)

            # Mark worker as idle again
            if completed_task.assigned_worker and completed_task.assigned_worker in controller_workers:
                controller_workers[completed_task.assigned_worker].status = WorkerStatus.IDLE

            print(f"  [Controller] Task {completed_task.id}: {completed_task.status.value}")
            print(f"               Result: {completed_task.result}")

        # Check if done
        if task_queue.is_empty() and all(w.status == WorkerStatus.IDLE for w in controller_workers.values()):
            # Give a moment for stragglers
            time.sleep(0.5)
            while not result_queue.empty():
                completed_task = result_queue.get_nowait()
                memory.store_result(completed_task)
                if completed_task.assigned_worker in controller_workers:
                    controller_workers[completed_task.assigned_worker].status = WorkerStatus.IDLE
                print(f"  [Controller] Task {completed_task.id}: {completed_task.status.value}")
                print(f"               Result: {completed_task.result}")
            break

        time.sleep(0.3)

    # --- Shutdown ---
    print("\n--- Shutting down workers ---")
    wm.shutdown_all()

    # --- Memory dump ---
    print("\n--- Memory Store ---")
    for entry in memory.dump():
        print(f"  {entry['task_id']} | {entry['skill']} | {entry['status']} | {entry['timestamp']}")

    print(f"\n  Total tasks processed: {len(memory.dump())}")
    print(f"  Skills registered: {skill_registry.list_skills()}")
    print("\n" + "=" * 60)
    print("  Kernel demo complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
