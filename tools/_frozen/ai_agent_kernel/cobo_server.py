#!/usr/bin/env python3
"""
Cobo gRPC Server — CCP Protocol Task Executor

Receives tasks from Ceiba via bidirectional gRPC stream.
Executes tasks, streams progress updates, handles retries, logs to CMP.

Usage:
  python3 cobo_server.py                    # start on default port 50051
  python3 cobo_server.py --port 50052       # custom port
  python3 cobo_server.py --demo             # run with simulated task failures

Requires: pip install grpcio grpcio-tools
Proto compile: python -m grpc_tools.protoc -I proto --python_out=. --grpc_python_out=. proto/ccp.proto
"""

import sys
import os
import grpc
from concurrent import futures
import time
import uuid
import json
import argparse
import importlib
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import ccp_pb2
import ccp_pb2_grpc

# ============ Configuration ============
DEFAULT_PORT = 50051
MAX_WORKERS = 10
TASK_STEP_DELAY = 0.5  # seconds between progress updates (simulated)
SIMULATE_FAILURES = False  # set True for testing retry logic

# In-memory task store — holds task context for retries
# Format: { task_id: { "task_type": str, "params": dict, "attempts": int, "status": str } }
import threading
TASK_STORE = {}
TASK_STORE_LOCK = threading.Lock()


# ============ CMP Logging ============
def log_to_cmp(task_id, status, message=""):
    timestamp = datetime.now(timezone.utc).isoformat()
    print(f"  [CMP {timestamp[:19]}] {task_id[:8]}.. {status}: {message}")
    # In production: POST to CMP endpoint or append to log file


# ============ Skill Executor ============
class SkillExecutor:
    """Executes tasks by routing to skill modules or built-in handlers."""

    # Built-in task handlers
    HANDLERS = {}

    @classmethod
    def register_handler(cls, task_type, handler):
        cls.HANDLERS[task_type] = handler

    @classmethod
    def execute(cls, task_type, params, progress_callback=None):
        """
        Execute a task. Returns (success, result_dict, error_msg).
        progress_callback(percent, detail) is called during execution.
        """
        # Check built-in handlers first
        if task_type in cls.HANDLERS:
            return cls.HANDLERS[task_type](params, progress_callback)

        # Try dynamic skill import
        try:
            skill_module = importlib.import_module(f"skills.{task_type}")
            if hasattr(skill_module, "run"):
                result = skill_module.run(**params)
                return True, result, None
        except ModuleNotFoundError:
            pass

        # Default: demo execution with progress simulation
        return cls._demo_execute(task_type, params, progress_callback)

    @classmethod
    def _demo_execute(cls, task_type, params, progress_callback=None):
        """Simulated execution — shows progress, returns mock result."""
        steps = 5
        for i in range(1, steps + 1):
            time.sleep(TASK_STEP_DELAY)
            pct = int((i / steps) * 100)
            if progress_callback:
                progress_callback(pct, f"Step {i}/{steps}: processing {task_type}")

        result = {
            "task_type": task_type,
            "params_received": params,
            "items_processed": len(params),
            "executor": "demo",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        return True, result, None


# ============ Built-in Handlers ============
def handle_shell(params, progress_cb=None):
    """Execute a shell command with safety checks."""
    import subprocess
    import shlex
    cmd = params.get("command", "echo 'no command'")

    # Allowlist of safe command prefixes
    ALLOWED_PREFIXES = {"echo", "ls", "cat", "head", "tail", "wc", "date", "whoami",
                        "pwd", "df", "du", "uptime", "hostname", "python3", "pip",
                        "node", "npm", "git"}
    # Block dangerous patterns
    BLOCKED_PATTERNS = {"rm -rf", "sudo", "chmod", "chown", "mkfs", "dd if=",
                        "curl | sh", "wget | sh", "> /dev/", "eval ", "exec "}

    cmd_lower = cmd.lower().strip()

    # Check blocked patterns
    for blocked in BLOCKED_PATTERNS:
        if blocked in cmd_lower:
            return False, None, f"Blocked command pattern: {blocked}"

    # Check allowlist (first word of command)
    first_word = cmd_lower.split()[0] if cmd_lower else ""
    if first_word not in ALLOWED_PREFIXES:
        return False, None, f"Command '{first_word}' not in allowlist. Allowed: {', '.join(sorted(ALLOWED_PREFIXES))}"

    if progress_cb:
        progress_cb(10, f"Running: {cmd[:50]}")
    try:
        # Use shlex.split to avoid shell=True injection
        args = shlex.split(cmd)
        result = subprocess.run(
            args, shell=False, capture_output=True, text=True, timeout=30
        )
        if progress_cb:
            progress_cb(100, "Command complete")
        return True, {
            "stdout": result.stdout[:2000],
            "stderr": result.stderr[:500],
            "returncode": result.returncode,
        }, None
    except subprocess.TimeoutExpired:
        return False, None, "Command timed out after 30s"
    except Exception as e:
        return False, None, str(e)


def handle_scrape(params, progress_cb=None):
    """Web scraping handler — delegates to skills.web_scraper module."""
    url = params.get("url", "unknown")
    mode = params.get("mode", "simple")
    if progress_cb:
        progress_cb(10, f"Scraping {url} (mode={mode})")
    try:
        from skills.web_scraper import run as scrape_run
        result = scrape_run(url=url, mode=mode, max_chars=params.get("max_chars", "10000"))
        if "error" in result:
            if progress_cb:
                progress_cb(100, f"Scrape failed: {result['error']}")
            return False, result, result["error"]
        if progress_cb:
            progress_cb(100, f"Scraped {result.get('text_length', 0)} chars")
        return True, result, None
    except Exception as e:
        return False, None, str(e)


# Register built-in handlers
SkillExecutor.register_handler("shell", handle_shell)
SkillExecutor.register_handler("scrape", handle_scrape)


# ============ gRPC Servicer ============
class CoboServicer(ccp_pb2_grpc.CeibaCoboServicer):
    """Cobo task executor — receives tasks from Ceiba, streams results."""

    def _make_header(self, correlation_id=""):
        return ccp_pb2.Header(
            version="1.0",
            message_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            source="Cobo",
            destination="Ceiba",
            correlation_id=correlation_id,
        )

    def _status_msg(self, task_id, status, progress, detail, correlation_id):
        return ccp_pb2.TaskMessage(
            header=self._make_header(correlation_id),
            status_update=ccp_pb2.TaskStatusUpdate(
                task_id=task_id,
                status=status,
                progress=progress,
                detail=detail,
            ),
        )

    def _execute_and_stream(self, task_id, task_type, params, correlation_id, memory_hook):
        """Run task, yield progress messages, then yield result or error."""

        # Initial status: RUNNING
        yield self._status_msg(task_id, ccp_pb2.RUNNING, 0, "Task accepted", correlation_id)

        start_time = time.time()

        # Simulate failure for testing
        if SIMULATE_FAILURES and TASK_STORE.get(task_id, {}).get("attempts", 0) < 2:
            time.sleep(0.5)
            yield ccp_pb2.TaskMessage(
                header=self._make_header(correlation_id),
                error=ccp_pb2.TaskError(
                    task_id=task_id,
                    error_code=500,
                    message="Simulated failure for retry testing",
                    retryable=True,
                ),
            )
            if memory_hook:
                log_to_cmp(task_id, "FAILED", "Simulated failure")
            return

        # Execute via SkillExecutor — collect progress updates
        progress_updates = []

        def progress_callback(pct, detail):
            progress_updates.append((pct, detail))

        success, result, error_msg = SkillExecutor.execute(task_type, params, progress_callback)

        # Stream collected progress updates
        for pct, detail in progress_updates:
            yield self._status_msg(task_id, ccp_pb2.RUNNING, pct, detail, correlation_id)

        runtime_ms = int((time.time() - start_time) * 1000)

        if success:
            result_json = json.dumps(result) if result else "{}"
            yield ccp_pb2.TaskMessage(
                header=self._make_header(correlation_id),
                result=ccp_pb2.TaskResult(
                    task_id=task_id,
                    success=True,
                    result_json=result_json,
                    runtime_ms=runtime_ms,
                    metadata={"executor": "cobo", "progress_updates": str(len(progress_updates))},
                ),
            )
            with TASK_STORE_LOCK:
                stored = TASK_STORE.get(task_id, {})
                TASK_STORE[task_id] = {**stored, "status": "COMPLETED", "runtime_ms": runtime_ms}
            print(f"[Cobo] Task {task_id[:8]}.. COMPLETED in {runtime_ms}ms")
            if memory_hook:
                log_to_cmp(task_id, "COMPLETED", result_json[:200])
        else:
            yield ccp_pb2.TaskMessage(
                header=self._make_header(correlation_id),
                error=ccp_pb2.TaskError(
                    task_id=task_id,
                    error_code=500,
                    message=error_msg or "Unknown error",
                    retryable=True,
                ),
            )
            with TASK_STORE_LOCK:
                stored = TASK_STORE.get(task_id, {})
                TASK_STORE[task_id] = {**stored, "status": "FAILED"}
            print(f"[Cobo] Task {task_id[:8]}.. FAILED: {error_msg}")
            if memory_hook:
                log_to_cmp(task_id, "FAILED", error_msg or "")

    def TaskStream(self, request_iterator, context):
        """Main bidirectional stream handler."""
        for msg in request_iterator:
            body_type = msg.WhichOneof("body")
            correlation_id = msg.header.correlation_id

            if body_type == "task_init":
                task = msg.task_init
                task_id = task.task_id
                params = dict(task.parameters)
                with TASK_STORE_LOCK:
                    TASK_STORE[task_id] = {
                        "task_type": task.task_type,
                        "params": params,
                        "attempts": 1,
                        "status": "RUNNING",
                        "memory_hook": task.memory_hook,
                    }

                print(f"\n[Cobo] Received task: {task_id[:8]}.. type={task.task_type}")
                print(f"  Description: {task.description}")
                print(f"  Priority: {task.priority} | Timeout: {task.timeout_ms}ms")

                # Stream execution progress and result
                for response in self._execute_and_stream(
                    task_id, task.task_type, params, correlation_id, task.memory_hook
                ):
                    yield response

            elif body_type == "retry_request":
                retry = msg.retry_request
                task_id = retry.task_id
                attempt = retry.attempt
                print(f"\n[Cobo] Retry request: {task_id[:8]}.. attempt {attempt}/{retry.max_attempts}")
                print(f"  Reason: {retry.reason}")

                if attempt > retry.max_attempts:
                    print(f"[Cobo] Max retries exceeded for {task_id[:8]}..")
                    yield ccp_pb2.TaskMessage(
                        header=self._make_header(correlation_id),
                        error=ccp_pb2.TaskError(
                            task_id=task_id,
                            error_code=429,
                            message=f"Max retries ({retry.max_attempts}) exceeded",
                            retryable=False,
                        ),
                    )
                    with TASK_STORE_LOCK:
                        TASK_STORE[task_id] = {**TASK_STORE.get(task_id, {}), "status": "PERMANENTLY_FAILED"}
                    log_to_cmp(task_id, "PERMANENTLY_FAILED", "Max retries exceeded")
                    continue

                # Recover original task context from store
                with TASK_STORE_LOCK:
                    stored = TASK_STORE.get(task_id, {})
                    task_type = stored.get("task_type", "unknown")
                    params = stored.get("params", {})
                    memory_hook = stored.get("memory_hook", True)
                    TASK_STORE[task_id] = {**stored, "attempts": attempt, "status": "RUNNING"}

                print(f"  Recovered context: type={task_type}, params={len(params)} keys")
                for response in self._execute_and_stream(
                    task_id, task_type, params, correlation_id, memory_hook
                ):
                    yield response

            elif body_type == "heartbeat":
                yield ccp_pb2.TaskMessage(
                    header=self._make_header(correlation_id),
                    heartbeat=ccp_pb2.Heartbeat(
                        source="Cobo",
                        status="alive",
                        timestamp=datetime.now(timezone.utc).isoformat(),
                    ),
                )


# ============ Server ============
def serve(port=DEFAULT_PORT, demo_failures=False):
    global SIMULATE_FAILURES
    SIMULATE_FAILURES = demo_failures

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=MAX_WORKERS))
    ccp_pb2_grpc.add_CeibaCoboServicer_to_server(CoboServicer(), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()

    print("=" * 50)
    print(f"  Cobo gRPC Server — CCP Protocol v1.0")
    print(f"  Port: {port} | Workers: {MAX_WORKERS}")
    print(f"  Demo failures: {demo_failures}")
    print(f"  Registered handlers: {list(SkillExecutor.HANDLERS.keys())}")
    print("=" * 50)
    print("[Cobo] Waiting for tasks from Ceiba...\n")

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("\n[Cobo] Shutting down...")
        server.stop(grace=5)
        print(f"[Cobo] Tasks processed: {len(TASK_STORE)}")


def main():
    parser = argparse.ArgumentParser(description="Cobo CCP Server")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--demo", action="store_true", help="Simulate failures for retry testing")
    args = parser.parse_args()
    serve(port=args.port, demo_failures=args.demo)


if __name__ == "__main__":
    main()
