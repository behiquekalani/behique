#!/usr/bin/env python3
"""
Ceiba Agent Kernel — Distributed AI Task Orchestrator
Runs on Computer 1 (Mac). Routes work to Cobo (Windows) via bridge.
Manages task queue, memory, routing, and skill registry.

Usage:
    python3 agent_kernel.py              # Run kernel loop (polls inbox)
    python3 agent_kernel.py submit <json> # Submit a task from CLI
    python3 agent_kernel.py status        # Show queue status
"""

import os
import json
import time
import uuid
import sys
import re
import requests
from pathlib import Path
from datetime import datetime

# ===============================
# CONFIG
# ===============================

ROOT = Path(__file__).resolve().parent.parent

TASK_INBOX = ROOT / "tasks" / "inbox"
TASK_ACTIVE = ROOT / "tasks" / "active"
TASK_DONE = ROOT / "tasks" / "done"

MEMORY_DIR = ROOT / "memory"
MEM_KNOWLEDGE = MEMORY_DIR / "knowledge"
MEM_EXPERIMENTS = MEMORY_DIR / "experiments"
MEM_PROJECTS = MEMORY_DIR / "projects"
MEM_SKILLS = MEMORY_DIR / "skills"

SKILLS_REGISTRY = ROOT / "skills" / "registry.json"

POLL_INTERVAL = 3  # seconds between inbox checks

# ===============================
# AI ENDPOINTS (real infrastructure)
# ===============================

# Cobo bridge — Node.js HTTP server on Windows (Computer 2)
BRIDGE_URL = "http://192.168.0.151:9876"
BRIDGE_TOKEN = os.getenv("BRIDGE_TOKEN", "")

# Ollama on Cobo — free local LLM
OLLAMA_URL = "http://192.168.0.151:11434/api/generate"
OLLAMA_MODEL = "llama3.2"

# OpenClaw agent command template (runs on Cobo via bridge)
OPENCLAW_CMD = 'openclaw agent --agent main --local --message "{prompt}" --json --timeout 120 2>&1'

# ===============================
# UTILITIES
# ===============================


def ensure_dirs():
    for p in [
        TASK_INBOX, TASK_ACTIVE, TASK_DONE,
        MEM_KNOWLEDGE, MEM_EXPERIMENTS, MEM_PROJECTS, MEM_SKILLS,
    ]:
        p.mkdir(parents=True, exist_ok=True)


def generate_task_id():
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    short = uuid.uuid4().hex[:6]
    return f"{ts}-{short}"


def load_json(path):
    with open(path, "r") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")

# ===============================
# MEMORY SYSTEM
# ===============================


def memory_search(query, limit=5):
    """Search all memory files for relevant context."""
    results = []
    query_lower = query.lower()
    query_words = set(query_lower.split())

    for mem_dir in [MEM_KNOWLEDGE, MEM_EXPERIMENTS, MEM_PROJECTS, MEM_SKILLS]:
        for f in mem_dir.glob("*.md"):
            try:
                text = f.read_text()
                text_lower = text.lower()
                # Score by word overlap
                score = sum(1 for w in query_words if w in text_lower)
                if score > 0:
                    results.append((score, text[:500], f.name))
            except Exception:
                pass

    results.sort(key=lambda x: x[0], reverse=True)
    return [(text, name) for _, text, name in results[:limit]]


def memory_write(entries):
    """Store discoveries from worker output."""
    type_dirs = {
        "knowledge": MEM_KNOWLEDGE,
        "experiment": MEM_EXPERIMENTS,
        "project": MEM_PROJECTS,
        "skill": MEM_SKILLS,
    }

    for entry in entries:
        mem_type = entry.get("type", "knowledge")
        content = entry.get("content", "")
        if not content:
            continue

        target_dir = type_dirs.get(mem_type, MEM_KNOWLEDGE)
        # Use first few words as filename
        slug = re.sub(r'[^a-z0-9]+', '-', content[:50].lower()).strip('-')
        filename = f"{slug}.md"
        path = target_dir / filename

        try:
            path.write_text(content)
            log(f"  Memory stored: {mem_type}/{filename}")
        except Exception as e:
            log(f"  Memory write failed: {e}")


def inject_memory_context(task):
    """Search memory and build context string for AI prompt."""
    memories = memory_search(task.objective)
    if not memories:
        return ""

    lines = ["\nRelevant knowledge from memory:"]
    for text, name in memories:
        lines.append(f"- [{name}] {text}")
    return "\n".join(lines)

# ===============================
# AI EXECUTION
# ===============================


def run_ollama(prompt):
    """Send prompt to Ollama on Cobo. Free, fast, good for simple tasks."""
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }
    try:
        r = requests.post(OLLAMA_URL, json=payload, timeout=120)
        data = r.json()
        return data.get("response", "")
    except Exception as e:
        return f"[OLLAMA ERROR] {e}"


def run_openclaw(prompt):
    """Send prompt to GPT-4o via OpenClaw on Cobo. Heavy reasoning."""
    escaped = prompt.replace('"', '\\"').replace('\n', ' ')
    cmd = OPENCLAW_CMD.format(prompt=escaped)

    payload = {"command": cmd}
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {BRIDGE_TOKEN}",
    }

    try:
        r = requests.post(BRIDGE_URL, json=payload, headers=headers, timeout=300)
        data = r.json()
        stdout = data.get("stdout", "")

        # Try to extract OpenClaw agent response
        try:
            match = re.search(r'\{.*"payloads".*\}', stdout, re.DOTALL)
            if match:
                oc_data = json.loads(match.group())
                payloads = oc_data.get("payloads", [])
                if payloads:
                    return payloads[0].get("text", stdout)
        except Exception:
            pass

        return stdout if stdout else data.get("stderr", "[no output]")
    except Exception as e:
        return f"[OPENCLAW ERROR] {e}"


def run_bridge_command(cmd):
    """Run an arbitrary shell command on Cobo via the bridge."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {BRIDGE_TOKEN}",
    }
    try:
        r = requests.post(BRIDGE_URL, json={"command": cmd}, headers=headers, timeout=60)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

# ===============================
# TASK ROUTING
# ===============================

# Tasks containing these keywords go to Ollama (free)
CHEAP_KEYWORDS = [
    "summarize", "format", "extract", "classify", "clean",
    "list", "count", "evaluate", "score", "review output",
    "simple", "quick",
]

# Tasks containing these keywords go to GPT-4o (heavy)
HEAVY_KEYWORDS = [
    "design", "architect", "debug", "implement", "code",
    "build", "analyze", "research", "create module",
    "write function", "fix bug", "refactor",
]


def route_task(task):
    """Decide which AI model handles this task."""
    prefs = task.model_preference

    # Explicit preference wins
    if "ollama" in prefs:
        return "ollama"
    if "gpt4o" in prefs or "openclaw" in prefs:
        return "openclaw"

    # Keyword-based routing
    obj = task.objective.lower()

    for kw in CHEAP_KEYWORDS:
        if kw in obj:
            return "ollama"

    for kw in HEAVY_KEYWORDS:
        if kw in obj:
            return "openclaw"

    # Default: use GPT-4o for unknown tasks (better reasoning)
    return "openclaw"

# ===============================
# TASK EXECUTION
# ===============================


def execute_ai_task(task):
    """Build prompt, inject memory, route to AI, return output."""
    memory_context = inject_memory_context(task)

    prompt = f"""You are an AI worker node in a distributed cluster.

Objective: {task.objective}

Context: {task.context}
{memory_context}

Respond in valid JSON with this structure:
{{
  "result": "your answer or output here",
  "spawn_tasks": [],
  "memory_write": []
}}

If you discover something useful, add it to memory_write:
{{"type": "knowledge", "content": "what you learned"}}

If this task should create subtasks, add them to spawn_tasks:
{{"objective": "subtask description", "model_preference": ["ollama"]}}
"""

    route = route_task(task)
    log(f"  Routed to: {route}")

    if route == "ollama":
        output = run_ollama(prompt)
    else:
        output = run_openclaw(prompt)

    return output


def process_ai_output(raw_output):
    """Parse AI response, extract memory writes and spawn requests."""
    try:
        # Try to find JSON in the output
        json_match = re.search(r'\{[\s\S]*\}', raw_output)
        if json_match:
            data = json.loads(json_match.group())
        else:
            data = {"result": raw_output}

        memory_entries = data.get("memory_write", [])
        if memory_entries:
            memory_write(memory_entries)

        return {
            "result": data.get("result", raw_output),
            "spawn_tasks": data.get("spawn_tasks", []),
        }
    except (json.JSONDecodeError, Exception):
        return {
            "result": raw_output,
            "spawn_tasks": [],
        }

# ===============================
# TASK OBJECT
# ===============================


class Task:
    def __init__(self, data):
        self.data = data
        self.task_id = data.get("task_id", generate_task_id())
        self.objective = data.get("objective", "")
        self.context = data.get("context", "")
        self.model_preference = data.get("model_preference", [])
        self.spawn_allowed = data.get("spawn_allowed", False)
        self.parent_task = data.get("parent_task", None)

    def to_dict(self):
        d = {
            "task_id": self.task_id,
            "objective": self.objective,
            "context": self.context,
            "model_preference": self.model_preference,
            "spawn_allowed": self.spawn_allowed,
        }
        if self.parent_task:
            d["parent_task"] = self.parent_task
        return d

# ===============================
# TASK QUEUE
# ===============================


class TaskQueue:

    def get_next_task(self):
        tasks = sorted(TASK_INBOX.glob("*.json"))
        if not tasks:
            return None

        task_file = tasks[0]
        data = load_json(task_file)
        active_path = TASK_ACTIVE / task_file.name
        task_file.rename(active_path)
        return Task(data), active_path

    def complete_task(self, task_path, result):
        done_path = TASK_DONE / task_path.name
        save_json(done_path, result)
        if task_path.exists():
            task_path.unlink()

    def submit_task(self, task_data):
        task_id = task_data.get("task_id", generate_task_id())
        task_data["task_id"] = task_id
        path = TASK_INBOX / f"{task_id}.json"
        save_json(path, task_data)
        log(f"  Submitted task: {task_id} — {task_data.get('objective', '')[:60]}")
        return task_id

    def status(self):
        inbox = list(TASK_INBOX.glob("*.json"))
        active = list(TASK_ACTIVE.glob("*.json"))
        done = list(TASK_DONE.glob("*.json"))
        return {
            "inbox": len(inbox),
            "active": len(active),
            "done": len(done),
            "inbox_tasks": [f.stem for f in inbox],
            "active_tasks": [f.stem for f in active],
        }

# ===============================
# SUBTASK SPAWNING
# ===============================


def submit_subtasks(queue, parent_task, subtasks):
    """Create child tasks from worker output."""
    for sub in subtasks:
        task_data = {
            "task_id": generate_task_id(),
            "parent_task": parent_task.task_id,
            "objective": sub.get("objective", ""),
            "context": sub.get("context", ""),
            "model_preference": sub.get("model_preference", []),
            "spawn_allowed": sub.get("spawn_allowed", False),
        }
        queue.submit_task(task_data)

# ===============================
# SKILL REGISTRY
# ===============================


def load_skills():
    if not SKILLS_REGISTRY.exists():
        return {"skills": []}
    return load_json(SKILLS_REGISTRY)


def save_skills(data):
    save_json(SKILLS_REGISTRY, data)


def register_skill(name, description, version=1, score=0.0):
    data = load_skills()
    # Update if exists
    for s in data["skills"]:
        if s["name"] == name:
            s["description"] = description
            s["version"] = version
            s["score"] = score
            save_skills(data)
            return
    # Add new
    data["skills"].append({
        "name": name,
        "description": description,
        "version": version,
        "score": score,
    })
    save_skills(data)

# ===============================
# KERNEL
# ===============================


class AgentKernel:

    def __init__(self):
        ensure_dirs()
        self.queue = TaskQueue()

    def run(self):
        """Main loop — poll inbox, execute tasks."""
        log("Agent Kernel started. Watching inbox...")
        log(f"  Inbox:  {TASK_INBOX}")
        log(f"  Bridge: {BRIDGE_URL}")
        log(f"  Ollama: {OLLAMA_URL}")

        while True:
            result = self.queue.get_next_task()
            if result is None:
                time.sleep(POLL_INTERVAL)
                continue

            task_obj, path = result
            log(f"Processing: {task_obj.task_id}")
            log(f"  Objective: {task_obj.objective[:80]}")

            task_result = self.execute_task(task_obj)
            self.queue.complete_task(path, task_result)

            log(f"Completed: {task_obj.task_id}")
            result_preview = str(task_result.get("result", ""))[:200]
            log(f"  Result: {result_preview}")
            spawned = task_result.get("spawned", 0)
            if spawned:
                log(f"  Spawned {spawned} subtask(s)")
            log("---")

    def execute_task(self, task):
        """Execute a single task through the AI pipeline."""
        started = datetime.now().isoformat()

        raw_output = execute_ai_task(task)
        processed = process_ai_output(raw_output)

        # Handle subtask spawning
        spawn_tasks = processed.get("spawn_tasks", [])
        if spawn_tasks and task.spawn_allowed:
            submit_subtasks(self.queue, task, spawn_tasks)

        return {
            "task_id": task.task_id,
            "objective": task.objective,
            "result": processed.get("result"),
            "spawned": len(spawn_tasks) if task.spawn_allowed else 0,
            "started": started,
            "completed": datetime.now().isoformat(),
        }

    def run_single(self, task_data):
        """Execute one task immediately (no queue)."""
        task = Task(task_data)
        log(f"Running single task: {task.objective[:80]}")
        result = self.execute_task(task)
        # Save to done
        done_path = TASK_DONE / f"{task.task_id}.json"
        save_json(done_path, result)
        return result

# ===============================
# CLI
# ===============================


def cli():
    ensure_dirs()

    if len(sys.argv) < 2:
        # Default: run kernel loop
        kernel = AgentKernel()
        kernel.run()
        return

    cmd = sys.argv[1]

    if cmd == "submit":
        # Submit task from CLI: python3 agent_kernel.py submit '{"objective":"..."}'
        if len(sys.argv) < 3:
            print("Usage: agent_kernel.py submit '{\"objective\": \"...\"}'")
            sys.exit(1)
        task_data = json.loads(sys.argv[2])
        queue = TaskQueue()
        tid = queue.submit_task(task_data)
        print(f"Submitted: {tid}")

    elif cmd == "status":
        queue = TaskQueue()
        s = queue.status()
        print(f"Inbox:  {s['inbox']} tasks")
        print(f"Active: {s['active']} tasks")
        print(f"Done:   {s['done']} tasks")
        if s["inbox_tasks"]:
            print(f"\nPending: {', '.join(s['inbox_tasks'])}")
        if s["active_tasks"]:
            print(f"Active:  {', '.join(s['active_tasks'])}")

    elif cmd == "run":
        # Run a single task immediately
        if len(sys.argv) < 3:
            print("Usage: agent_kernel.py run '{\"objective\": \"...\"}'")
            sys.exit(1)
        task_data = json.loads(sys.argv[2])
        kernel = AgentKernel()
        result = kernel.run_single(task_data)
        print(json.dumps(result, indent=2))

    elif cmd == "memory":
        # Search memory: python3 agent_kernel.py memory "search query"
        if len(sys.argv) < 3:
            print("Usage: agent_kernel.py memory 'search query'")
            sys.exit(1)
        results = memory_search(sys.argv[2])
        if results:
            for text, name in results:
                print(f"\n--- {name} ---")
                print(text)
        else:
            print("No matching memories found.")

    elif cmd == "skills":
        data = load_skills()
        if not data["skills"]:
            print("No skills registered.")
        for s in data["skills"]:
            print(f"  {s['name']} v{s['version']} (score: {s.get('score', 'n/a')})")
            print(f"    {s['description']}")

    else:
        print(f"Unknown command: {cmd}")
        print("Commands: submit, status, run, memory, skills")


if __name__ == "__main__":
    cli()
