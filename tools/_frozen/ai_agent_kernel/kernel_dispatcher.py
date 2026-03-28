#!/usr/bin/env python3
"""
Kernel Dispatcher — Bridges the Agent Kernel with gRPC CCP

Takes tasks from the Agent Kernel's TaskQueue and dispatches them
to Cobo over gRPC, or runs them locally as fallback.

This is the glue between:
  - main.py (Agent Kernel: TaskQueue, Scheduler, SkillRegistry)
  - ceiba_client.py (gRPC client with retry + CMP)

Usage:
  python3 kernel_dispatcher.py              # demo: queue 3 tasks, dispatch to Cobo
  python3 kernel_dispatcher.py --local      # run all tasks locally (no gRPC)
  python3 kernel_dispatcher.py --host 192.168.0.151  # dispatch to remote Cobo
"""

import sys
import os
import json
import time
import argparse
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import TaskQueue, Task, TaskPriority, TaskStatus, SkillRegistry, Skill, MemoryInterface, execute_task
from ceiba_client import CeibaClient, CMPLogger
from cmp import CMP


class KernelDispatcher:
    """
    Dispatches tasks from the Agent Kernel queue to either:
    1. Cobo via gRPC (remote execution)
    2. Local execution (fallback when Cobo is offline)
    """

    def __init__(self, host="localhost", port=50051, local_only=False):
        self.task_queue = TaskQueue()
        self.skill_registry = SkillRegistry()
        self.memory = MemoryInterface()
        self.cmp = CMPLogger()
        self.local_only = local_only
        self.client = None
        self.results = []

        if not local_only:
            self.client = CeibaClient(host, port)

    def register_skill(self, name, description="", version="1.0"):
        self.skill_registry.register_skill(Skill(
            name=name,
            description=description,
            version=version,
            executor_module=name,
        ))

    def add_task(self, skill, params, priority=TaskPriority.MEDIUM, description=""):
        """Add a task to the kernel queue."""
        task = Task(
            skill=skill,
            input_data=params,
            priority=priority,
        )
        self.task_queue.push(task)
        self.cmp.log(task.id, "QUEUED", f"skill={skill}, priority={priority}")
        return task.id

    def dispatch_all(self):
        """Process all tasks in the queue."""
        print("\n" + "=" * 60)
        print("  Kernel Dispatcher — Processing Queue")
        print(f"  Mode: {'LOCAL' if self.local_only else 'REMOTE (gRPC → Cobo)'}")
        print(f"  Tasks: {self.task_queue.size()}")
        print("=" * 60 + "\n")

        if not self.local_only:
            try:
                self.client.connect()
            except Exception as e:
                print(f"[Dispatcher] Cannot connect to Cobo: {e}")
                print("[Dispatcher] Falling back to local execution\n")
                self.local_only = True

        processed = 0
        failed = 0

        while not self.task_queue.is_empty():
            task = self.task_queue.pop()
            task.status = TaskStatus.RUNNING
            processed += 1

            print(f"\n--- Task {processed}: {task.id} (skill={task.skill}, priority={task.priority}) ---")

            if self.local_only:
                # Local execution via Agent Kernel
                completed = execute_task(task)
                self.memory.store_result(completed)
                self.results.append({
                    "task_id": completed.id,
                    "skill": completed.skill,
                    "status": completed.status.value,
                    "result": completed.result,
                    "mode": "local",
                })
                if completed.status == TaskStatus.FAILED:
                    failed += 1
            else:
                # Remote execution via gRPC
                params = {k: str(v) for k, v in task.input_data.items()}
                success, result = self.client.send_task(
                    task_type=task.skill,
                    params=params,
                    description=f"Kernel task {task.id}: {task.skill}",
                    priority="high" if task.priority >= TaskPriority.HIGH else "medium",
                )
                task.status = TaskStatus.COMPLETED if success else TaskStatus.FAILED
                task.result = result
                self.memory.store_result(task)
                self.results.append({
                    "task_id": task.id,
                    "skill": task.skill,
                    "status": task.status.value,
                    "result": result,
                    "mode": "remote",
                })
                if not success:
                    failed += 1

        if self.client:
            self.client.close()

        # Summary
        print("\n" + "=" * 60)
        print("  Dispatch Summary")
        print(f"  Total: {processed} | Success: {processed - failed} | Failed: {failed}")
        print(f"  CMP events: {len(self.cmp.events)}")
        print(f"  Memory entries: {len(self.memory.dump())}")
        print("=" * 60)

        return self.results


def main():
    parser = argparse.ArgumentParser(description="Kernel Dispatcher")
    parser.add_argument("--host", default="localhost", help="Cobo host")
    parser.add_argument("--port", type=int, default=50051, help="Cobo port")
    parser.add_argument("--local", action="store_true", help="Run all tasks locally")
    args = parser.parse_args()

    dispatcher = KernelDispatcher(
        host=args.host,
        port=args.port,
        local_only=args.local,
    )

    # Register skills
    dispatcher.register_skill("scrape", "Web scraping via Playwright")
    dispatcher.register_skill("shell", "Shell command execution")
    dispatcher.register_skill("skills.sample_skill", "Sample text processor")
    dispatcher.register_skill("skills.ebay_research", "eBay sold listing research")
    dispatcher.register_skill("skills.web_scraper", "URL scraping (HTTP + Playwright)")

    # Queue demo tasks
    dispatcher.add_task(
        skill="scrape",
        params={"url": "https://www.ebay.com/trending", "max_items": "50"},
        priority=TaskPriority.HIGH,
    )
    dispatcher.add_task(
        skill="shell",
        params={"command": "echo 'Hello from Ceiba Kernel'"},
        priority=TaskPriority.MEDIUM,
    )
    dispatcher.add_task(
        skill="skills.ebay_research",
        params={"query": "Funko Pop Vegeta", "condition": "New"},
        priority=TaskPriority.HIGH,
    )

    # Dispatch
    results = dispatcher.dispatch_all()

    # Print results
    print("\n--- Results ---")
    for r in results:
        print(f"  {r['task_id']} [{r['mode']}] {r['skill']}: {r['status']}")


if __name__ == "__main__":
    main()
