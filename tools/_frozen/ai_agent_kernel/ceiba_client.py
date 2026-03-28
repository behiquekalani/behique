#!/usr/bin/env python3
"""
Ceiba gRPC Client — CCP Protocol with Retry + CMP Logging

Production-ready client for triggering autonomous tasks on Cobo
with exponential backoff, MAX_RETRIES, and CMP memory hooks.

Usage:
  python3 ceiba_client.py                          # demo task
  python3 ceiba_client.py --type scrape --params '{"url":"https://ebay.com"}'

Requires: pip install grpcio grpcio-tools
Proto compile: python -m grpc_tools.protoc -I proto --python_out=. --grpc_python_out=. proto/ccp.proto
"""

import sys
import os
import grpc
import uuid
import time
import json
import argparse
import threading
from datetime import datetime, timezone

# Add parent dir to path for proto imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import ccp_pb2
import ccp_pb2_grpc

# ============ Configuration ============
MAX_RETRIES = 3
BASE_BACKOFF = 1.0  # seconds
BACKOFF_FACTOR = 2.0
HEARTBEAT_INTERVAL = 15  # seconds
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 50051


# ============ CMP Integration ============
try:
    from cmp import CMP as _CMP
    _CMP_AVAILABLE = True
except ImportError:
    _CMP_AVAILABLE = False


class CMPLogger:
    """CMP-backed logger. Falls back to JSONL if CMP unavailable."""

    def __init__(self, log_file=None):
        self.log_file = log_file or os.path.join(
            os.path.dirname(__file__), "cmp_log.jsonl"
        )
        self.events = []
        self.cmp = _CMP(author="ceiba") if _CMP_AVAILABLE else None
        if self.cmp:
            print("  [CMP] SQLite-backed memory protocol active")

    def log(self, task_id, status, message="", metadata=None):
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "task_id": task_id,
            "status": status,
            "message": message,
            "metadata": metadata or {},
        }
        self.events.append(event)
        print(f"  [CMP] {task_id[:8]}.. {status}: {message}")

        # Write to CMP SQLite if available
        if self.cmp:
            try:
                self.cmp.log_task(
                    task_id=task_id,
                    status=status,
                    payload={"message": message, **(metadata or {})},
                )
            except Exception:
                pass

        # Also append to JSONL as backup
        try:
            with open(self.log_file, "a") as f:
                f.write(json.dumps(event) + "\n")
        except Exception:
            pass

    def dump(self):
        return self.events

    def close(self):
        if self.cmp:
            self.cmp.close()


# ============ Message Builders ============
def make_header(correlation_id=""):
    return ccp_pb2.Header(
        version="1.0",
        message_id=str(uuid.uuid4()),
        timestamp=datetime.now(timezone.utc).isoformat(),
        source="Ceiba",
        destination="Cobo",
        correlation_id=correlation_id,
    )


def make_task_message(task_type, params, description="",
                      timeout_ms=30000, priority="medium", memory_hook=True):
    """Build a TASK_INIT message for Cobo."""
    task_id = str(uuid.uuid4())
    return ccp_pb2.TaskMessage(
        header=make_header(correlation_id=task_id),
        task_init=ccp_pb2.Task(
            task_id=task_id,
            task_type=task_type,
            description=description or f"{task_type} task",
            parameters=params,
            timeout_ms=timeout_ms,
            priority=priority,
            memory_hook=memory_hook,
        ),
    ), task_id


def make_retry_message(task_id, attempt, reason=""):
    return ccp_pb2.TaskMessage(
        header=make_header(correlation_id=task_id),
        retry_request=ccp_pb2.RetryRequest(
            task_id=task_id,
            reason=reason,
            attempt=attempt,
            max_attempts=MAX_RETRIES,
        ),
    )


def make_heartbeat():
    return ccp_pb2.TaskMessage(
        header=make_header(),
        heartbeat=ccp_pb2.Heartbeat(
            source="Ceiba",
            status="alive",
            timestamp=datetime.now(timezone.utc).isoformat(),
        ),
    )


# ============ Client ============
class CeibaClient:
    """gRPC client with retry logic, heartbeats, and CMP logging."""

    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT):
        self.host = host
        self.port = port
        self.cmp = CMPLogger()
        self.channel = None
        self.stub = None

    def connect(self):
        """Establish gRPC channel."""
        target = f"{self.host}:{self.port}"
        print(f"[Ceiba] Connecting to Cobo at {target}...")
        self.channel = grpc.insecure_channel(target)

        # Wait for channel to be ready (with timeout)
        try:
            grpc.channel_ready_future(self.channel).result(timeout=5)
            print(f"[Ceiba] Connected to Cobo at {target}")
        except grpc.FutureTimeoutError:
            print(f"[Ceiba] WARNING: Could not verify connection to {target}")

        self.stub = ccp_pb2_grpc.CeibaCoboStub(self.channel)

    def close(self):
        if self.channel:
            self.channel.close()

    def send_task(self, task_type, params, description="", timeout_ms=30000, priority="medium"):
        """
        Send a task to Cobo with full retry logic and CMP logging.
        Returns (success: bool, result: dict or None)
        """
        task_msg, task_id = make_task_message(
            task_type, params, description, timeout_ms, priority
        )

        print(f"\n[Ceiba] Sending task {task_id[:8]}.. type={task_type}")
        self.cmp.log(task_id, "INITIATED", f"type={task_type}, priority={priority}")

        attempt = 0
        current_msg = task_msg

        while attempt <= MAX_RETRIES:
            try:
                result = self._execute_stream(current_msg, task_id)
                if result is not None:
                    return True, result
                raise TimeoutError("Stream ended without result")

            except Exception as e:
                attempt += 1
                error_msg = str(e)

                if attempt > MAX_RETRIES:
                    print(f"[Ceiba] Task {task_id[:8]}.. PERMANENTLY FAILED after {MAX_RETRIES} retries")
                    self.cmp.log(task_id, "PERMANENTLY_FAILED", f"Max retries: {error_msg}")
                    return False, None

                backoff = BASE_BACKOFF * (BACKOFF_FACTOR ** (attempt - 1))
                print(f"[Ceiba] Retry {attempt}/{MAX_RETRIES} in {backoff:.1f}s — {error_msg}")
                self.cmp.log(task_id, "RETRYING", f"attempt={attempt}, backoff={backoff}s")
                time.sleep(backoff)

                # Build retry message
                current_msg = make_retry_message(task_id, attempt, error_msg)

        return False, None

    def _execute_stream(self, initial_msg, task_id):
        """Open bidirectional stream, send message, process responses."""
        response_holder = {"result": None, "error": None}
        stop_heartbeat = threading.Event()

        def request_iterator():
            # Send the initial message (task or retry)
            yield initial_msg

            # Keep sending heartbeats until stream ends
            while not stop_heartbeat.is_set():
                time.sleep(HEARTBEAT_INTERVAL)
                if not stop_heartbeat.is_set():
                    yield make_heartbeat()

        try:
            responses = self.stub.TaskStream(request_iterator())

            for response in responses:
                body_type = response.WhichOneof("body")

                if body_type == "status_update":
                    su = response.status_update
                    status_name = ccp_pb2.TaskStatus.Name(su.status)
                    detail = su.detail or ""
                    print(f"  [{status_name}] {su.progress}% — {detail}")
                    self.cmp.log(task_id, status_name, f"{su.progress}% {detail}")

                elif body_type == "result":
                    r = response.result
                    result_data = json.loads(r.result_json) if r.result_json else {}
                    print(f"  [RESULT] success={r.success} runtime={r.runtime_ms}ms")
                    self.cmp.log(task_id, "COMPLETED", r.result_json,
                                 metadata=dict(r.metadata))
                    stop_heartbeat.set()
                    return result_data

                elif body_type == "error":
                    e = response.error
                    print(f"  [ERROR] code={e.error_code}: {e.message} retryable={e.retryable}")
                    self.cmp.log(task_id, "FAILED", e.message)
                    stop_heartbeat.set()
                    if e.retryable:
                        raise Exception(f"Retryable error: {e.message}")
                    else:
                        return None  # Non-retryable = permanent failure

                elif body_type == "heartbeat":
                    hb = response.heartbeat
                    print(f"  [HEARTBEAT] {hb.source}: {hb.status}")

        except grpc.RpcError as e:
            stop_heartbeat.set()
            raise Exception(f"gRPC error: {e.code()}: {e.details()}")
        finally:
            stop_heartbeat.set()

        return None


# ============ CLI ============
def main():
    parser = argparse.ArgumentParser(description="Ceiba CCP Client — send tasks to Cobo")
    parser.add_argument("--host", default=DEFAULT_HOST, help="Cobo host")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Cobo port")
    parser.add_argument("--type", default="demo", help="Task type (e.g. scrape, shell, skill)")
    parser.add_argument("--params", default='{"message": "Hello from Ceiba"}',
                        help="JSON params string")
    parser.add_argument("--desc", default="", help="Task description")
    parser.add_argument("--priority", default="medium",
                        choices=["low", "medium", "high", "critical"])
    parser.add_argument("--timeout", type=int, default=30000, help="Timeout in ms")
    args = parser.parse_args()

    params = json.loads(args.params)

    client = CeibaClient(args.host, args.port)
    client.connect()

    try:
        success, result = client.send_task(
            task_type=args.type,
            params=params,
            description=args.desc,
            timeout_ms=args.timeout,
            priority=args.priority,
        )

        print("\n" + "=" * 50)
        if success:
            print(f"[Ceiba] Task completed successfully")
            print(f"  Result: {json.dumps(result, indent=2)}")
        else:
            print(f"[Ceiba] Task failed permanently")

        print(f"\n[CMP] {len(client.cmp.events)} events logged to cmp_log.jsonl")
        print("=" * 50)

    finally:
        client.close()


if __name__ == "__main__":
    main()
