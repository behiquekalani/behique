---
title: "ceiba-cobo-grpc-prototype"
type: design
tags: [ceiba-cobo, communication, protocol:]

projects:
  - Computer-2
systems:
  - SYS_Bridge
created: 2026-03-16
---

# Ceiba-Cobo Communication Protocol: Protobuf + gRPC Streaming Prototype

---

## 1. Proto Definition (ccp.proto)

```protobuf
syntax = "proto3";

package ccp;

// --- Header: attached to every message ---
message Header {
  string version      = 1;  // e.g. "1.0"
  string message_id   = 2;  // UUID
  string timestamp    = 3;  // ISO8601 UTC
  string source       = 4;  // "Ceiba" or "Cobo"
  string correlation_id = 5; // groups messages in a task lifecycle
}

// --- Task: sent by Ceiba to start work on Cobo ---
message Task {
  string task_id      = 1;
  string type         = 2;  // e.g. "browser_action", "scrape", "shell"
  string description  = 3;
  map<string, string> params = 4;
  int32 priority      = 5;  // 1 = low, 5 = critical
  int32 timeout_sec   = 6;
}

// --- Status update: sent by Cobo during execution ---
message TaskStatusUpdate {
  string task_id      = 1;
  string status       = 2;  // "queued", "running", "paused", "completed", "failed"
  float progress      = 3;  // 0.0 to 1.0
  string detail       = 4;
}

// --- Result: sent by Cobo when task completes ---
message TaskResult {
  string task_id      = 1;
  bool success        = 2;
  string output       = 3;  // serialized result payload
  map<string, string> metadata = 4;
}

// --- Error: sent by Cobo on failure ---
message TaskError {
  string task_id      = 1;
  string error_code   = 2;
  string message      = 3;
  bool retryable      = 4;
}

// --- Retry request: sent by Ceiba after a retryable failure ---
message RetryRequest {
  string task_id      = 1;
  int32 attempt       = 2;
  int32 max_attempts  = 3;
}

// --- Heartbeat: keeps stream alive, either direction ---
message Heartbeat {
  string source       = 1;
  string timestamp    = 2;
}

// --- Envelope: wraps all message types on the stream ---
message TaskMessage {
  Header header       = 1;

  oneof body {
    Task              task          = 2;
    TaskStatusUpdate  status_update = 3;
    TaskResult        result        = 4;
    TaskError         error         = 5;
    RetryRequest      retry         = 6;
    Heartbeat         heartbeat     = 7;
  }
}

// --- Service: single bidirectional stream ---
service CeibaCobo {
  rpc TaskStream (stream TaskMessage) returns (stream TaskMessage);
}
```

---

## 2. Python gRPC Client (Ceiba)

```python
import grpc
import uuid
import time
from datetime import datetime, timezone

import ccp_pb2
import ccp_pb2_grpc


def generate_task_message(task_id: str, task_type: str, description: str,
                          params: dict, priority: int = 3,
                          timeout_sec: int = 120) -> ccp_pb2.TaskMessage:
    """Build a TaskMessage envelope containing a new Task."""
    return ccp_pb2.TaskMessage(
        header=ccp_pb2.Header(
            version="1.0",
            message_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            source="Ceiba",
            correlation_id=task_id,
        ),
        task=ccp_pb2.Task(
            task_id=task_id,
            type=task_type,
            description=description,
            params=params,
            priority=priority,
            timeout_sec=timeout_sec,
        ),
    )


def ceiba_task_client(host: str = "bridge.merchoo.shop", port: int = 50051):
    """Open a bidirectional stream to Cobo, send a task, print responses."""
    channel = grpc.insecure_channel(f"{host}:{port}")
    stub = ccp_pb2_grpc.CeibaCoboStub(channel)

    task_id = str(uuid.uuid4())
    task_msg = generate_task_message(
        task_id=task_id,
        task_type="browser_action",
        description="Scrape eBay trending products page",
        params={"url": "https://www.ebay.com/trending", "max_items": "50"},
    )

    def request_iterator():
        # Send the task
        yield task_msg
        # Keep stream alive with heartbeats
        while True:
            time.sleep(15)
            yield ccp_pb2.TaskMessage(
                header=ccp_pb2.Header(
                    version="1.0",
                    message_id=str(uuid.uuid4()),
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    source="Ceiba",
                    correlation_id=task_id,
                ),
                heartbeat=ccp_pb2.Heartbeat(
                    source="Ceiba",
                    timestamp=datetime.now(timezone.utc).isoformat(),
                ),
            )

    responses = stub.TaskStream(request_iterator())

    for response in responses:
        body_type = response.WhichOneof("body")
        if body_type == "status_update":
            su = response.status_update
            print(f"[{su.status}] {su.task_id} — {su.progress*100:.0f}% — {su.detail}")
        elif body_type == "result":
            r = response.result
            print(f"[RESULT] {r.task_id} — success={r.success}")
            print(f"  output: {r.output[:200]}")
            break
        elif body_type == "error":
            e = response.error
            print(f"[ERROR] {e.task_id} — {e.error_code}: {e.message}")
            if e.retryable:
                print("  -> retryable, sending retry request")
            break
        elif body_type == "heartbeat":
            print(f"[HEARTBEAT] from {response.heartbeat.source}")


if __name__ == "__main__":
    ceiba_task_client()
```

---

## 3. Python gRPC Server (Cobo)

```python
import grpc
from concurrent import futures
import uuid
import time
from datetime import datetime, timezone

import ccp_pb2
import ccp_pb2_grpc


class CoboServicer(ccp_pb2_grpc.CeibaCoboServicer):
    """Cobo task executor — receives tasks, streams progress, returns results."""

    def _make_header(self, correlation_id: str) -> ccp_pb2.Header:
        return ccp_pb2.Header(
            version="1.0",
            message_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            source="Cobo",
            correlation_id=correlation_id,
        )

    def TaskStream(self, request_iterator, context):
        for message in request_iterator:
            body_type = message.WhichOneof("body")

            if body_type == "task":
                task = message.task
                correlation_id = message.header.correlation_id
                print(f"[COBO] Received task: {task.task_id} — {task.description}")

                # --- Queued ---
                yield ccp_pb2.TaskMessage(
                    header=self._make_header(correlation_id),
                    status_update=ccp_pb2.TaskStatusUpdate(
                        task_id=task.task_id,
                        status="queued",
                        progress=0.0,
                        detail="Task accepted, queued for execution",
                    ),
                )

                # --- Running with progress ---
                steps = 5
                for i in range(1, steps + 1):
                    time.sleep(1)  # simulate work
                    yield ccp_pb2.TaskMessage(
                        header=self._make_header(correlation_id),
                        status_update=ccp_pb2.TaskStatusUpdate(
                            task_id=task.task_id,
                            status="running",
                            progress=i / steps,
                            detail=f"Processing step {i}/{steps}",
                        ),
                    )

                # --- Result ---
                yield ccp_pb2.TaskMessage(
                    header=self._make_header(correlation_id),
                    result=ccp_pb2.TaskResult(
                        task_id=task.task_id,
                        success=True,
                        output='{"items_scraped": 50, "file": "/tmp/ebay_trending.json"}',
                        metadata={"duration_sec": "5", "executor": "playwright"},
                    ),
                )

            elif body_type == "heartbeat":
                # Echo heartbeat back
                yield ccp_pb2.TaskMessage(
                    header=self._make_header(message.header.correlation_id),
                    heartbeat=ccp_pb2.Heartbeat(
                        source="Cobo",
                        timestamp=datetime.now(timezone.utc).isoformat(),
                    ),
                )

            elif body_type == "retry":
                retry = message.retry
                print(f"[COBO] Retry request for {retry.task_id}, attempt {retry.attempt}")
                # Re-execute task logic here


def serve(port: int = 50051):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    ccp_pb2_grpc.add_CeibaCoboServicer_to_server(CoboServicer(), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    print(f"[COBO] gRPC server listening on port {port}")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
```

---

## 4. Advantages Over HTTP-Based CCP

| Feature | HTTP CCP | gRPC Streaming CCP |
|---------|----------|---------------------|
| Progress updates | Polling or webhooks | Real-time bidirectional stream |
| Retry mechanism | Manual HTTP retry logic | Built-in via RetryRequest on same stream |
| Type safety | JSON (loosely typed) | Protobuf strong typing, code generation |
| CMP hook integration | POST to logging endpoint | Intercept stream messages, log inline |
| Heartbeat | Separate endpoint or timer | Same stream, zero extra connections |
| Load balancer scalability | Standard HTTP LB | gRPC-aware LB (Envoy, etc.), multiplexed streams |
| Latency | HTTP overhead per request | Single persistent connection, binary protocol |

---

## CEIBA NOTES

- **Source:** ChatGPT (2026-03-16)
- **Status:** DESIGN — needs implementation
- Upgrades the HTTP-based CCP to production-grade gRPC
- **Needs:** `pip install grpcio grpcio-tools`
- **Compile proto:** `python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. ccp.proto`
- The existing bridge at `bridge.merchoo.shop:9876` can run alongside this or be replaced
- **Next:** Add retry manager with exponential backoff + CMP logging
