#!/usr/bin/env python3
"""
Ceiba Memory Protocol (CMP) — Production Implementation

Structured memory storage for the Behique AI agent cluster.
SQLite-backed with typed payloads, SHA256 integrity, conflict detection,
keyword search, version tracking, and access control.

Usage as library:
    from cmp import CMP
    cmp = CMP()
    entry_id = cmp.write("event", {"description": "Task completed"}, tags=["task"])
    results = cmp.query(keywords=["task"])

Usage as CLI:
    python3 cmp.py write --type event --payload '{"desc": "test"}' --tags task,demo
    python3 cmp.py query --keywords task
    python3 cmp.py get <entry_id>
    python3 cmp.py stats
    python3 cmp.py history --task-id <id>
    python3 cmp.py export --format jsonl
"""

import os
import sys
import uuid
import json
import time
import hashlib
import sqlite3
import argparse
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from enum import Enum


# ============ Constants ============
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cmp.db")
VALID_TYPES = {"event", "action", "metadata", "state", "task", "error", "conflict"}
RESOLUTION_STRATEGIES = {"lww", "merge", "manual"}


# ============ Data Models ============
class MemoryType(str, Enum):
    EVENT = "event"
    ACTION = "action"
    METADATA = "metadata"
    STATE = "state"
    TASK = "task"
    ERROR = "error"
    CONFLICT = "conflict"


@dataclass
class MemoryEntry:
    """A single CMP memory entry with integrity guarantees."""
    id: str
    type: str
    timestamp: str
    payload: Dict[str, Any]
    author: str
    version: int
    tags: List[str]
    permissions: Dict[str, List[str]]
    hash: str = ""
    correlation_id: str = ""  # links related entries (e.g. task lifecycle)

    def __post_init__(self):
        if not self.hash:
            self.hash = self.compute_hash()

    def compute_hash(self) -> str:
        """SHA256(payload_json + timestamp + author + version)"""
        content = (
            json.dumps(self.payload, sort_keys=True)
            + self.timestamp
            + self.author
            + str(self.version)
        )
        return hashlib.sha256(content.encode()).hexdigest()

    def verify_integrity(self) -> bool:
        """Check if stored hash matches computed hash."""
        return self.hash == self.compute_hash()

    def to_dict(self) -> Dict:
        d = asdict(self)
        return d

    @classmethod
    def from_dict(cls, d: Dict) -> "MemoryEntry":
        return cls(**d)

    @classmethod
    def create(cls, type: str, payload: Dict, author: str = "ceiba",
               tags: List[str] = None, correlation_id: str = "",
               permissions: Dict = None) -> "MemoryEntry":
        """Factory method — creates a new entry with auto-generated fields."""
        return cls(
            id=str(uuid.uuid4()),
            type=type,
            timestamp=datetime.now(timezone.utc).isoformat(),
            payload=payload,
            author=author,
            version=1,
            tags=tags or [],
            permissions=permissions or {"read": ["*"], "write": [author]},
            correlation_id=correlation_id,
        )


# ============ SQLite Storage Backend ============
class CMPStorage:
    """SQLite-backed storage with full-text search on tags and payload."""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                payload TEXT NOT NULL,
                author TEXT NOT NULL,
                version INTEGER NOT NULL DEFAULT 1,
                tags TEXT NOT NULL DEFAULT '[]',
                permissions TEXT NOT NULL DEFAULT '{}',
                hash TEXT NOT NULL,
                correlation_id TEXT DEFAULT '',
                created_at REAL NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_type ON memories(type);
            CREATE INDEX IF NOT EXISTS idx_author ON memories(author);
            CREATE INDEX IF NOT EXISTS idx_timestamp ON memories(timestamp);
            CREATE INDEX IF NOT EXISTS idx_correlation ON memories(correlation_id);

            CREATE TABLE IF NOT EXISTS conflicts (
                id TEXT PRIMARY KEY,
                memory_id TEXT NOT NULL,
                versions TEXT NOT NULL,
                resolved_by TEXT DEFAULT '',
                resolution_strategy TEXT DEFAULT '',
                resolved_at TEXT DEFAULT '',
                FOREIGN KEY (memory_id) REFERENCES memories(id)
            );
        """)
        self.conn.commit()

    def insert(self, entry: MemoryEntry) -> bool:
        """Insert a new memory entry. Returns True on success."""
        try:
            self.conn.execute(
                """INSERT INTO memories
                   (id, type, timestamp, payload, author, version, tags, permissions, hash, correlation_id, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    entry.id, entry.type, entry.timestamp,
                    json.dumps(entry.payload, sort_keys=True),
                    entry.author, entry.version,
                    json.dumps(entry.tags),
                    json.dumps(entry.permissions),
                    entry.hash, entry.correlation_id,
                    time.time(),
                )
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Duplicate ID

    def update(self, entry: MemoryEntry) -> bool:
        """Update an existing entry (new version)."""
        cursor = self.conn.execute(
            """UPDATE memories SET
               type=?, timestamp=?, payload=?, author=?, version=?,
               tags=?, permissions=?, hash=?, correlation_id=?
               WHERE id=?""",
            (
                entry.type, entry.timestamp,
                json.dumps(entry.payload, sort_keys=True),
                entry.author, entry.version,
                json.dumps(entry.tags),
                json.dumps(entry.permissions),
                entry.hash, entry.correlation_id,
                entry.id,
            )
        )
        self.conn.commit()
        return cursor.rowcount > 0

    def get(self, entry_id: str) -> Optional[MemoryEntry]:
        """Get a single entry by ID."""
        row = self.conn.execute("SELECT * FROM memories WHERE id=?", (entry_id,)).fetchone()
        if not row:
            return None
        return self._row_to_entry(row)

    def get_latest_version(self, entry_id: str) -> Optional[int]:
        """Get the latest version number for an entry."""
        row = self.conn.execute("SELECT version FROM memories WHERE id=?", (entry_id,)).fetchone()
        return row["version"] if row else None

    def query(self, keywords: List[str] = None, types: List[str] = None,
              author: str = None, correlation_id: str = None,
              time_from: str = None, time_to: str = None,
              limit: int = 50, offset: int = 0) -> List[MemoryEntry]:
        """Query memories with filters."""
        conditions = []
        params = []

        if types:
            placeholders = ",".join("?" * len(types))
            conditions.append(f"type IN ({placeholders})")
            params.extend(types)

        if author:
            conditions.append("author = ?")
            params.append(author)

        if correlation_id:
            conditions.append("correlation_id = ?")
            params.append(correlation_id)

        if time_from:
            conditions.append("timestamp >= ?")
            params.append(time_from)

        if time_to:
            conditions.append("timestamp <= ?")
            params.append(time_to)

        if keywords:
            # Search in tags JSON and payload JSON
            kw_conditions = []
            for kw in keywords:
                kw_conditions.append("(tags LIKE ? OR payload LIKE ?)")
                params.extend([f"%{kw}%", f"%{kw}%"])
            conditions.append("(" + " AND ".join(kw_conditions) + ")")

        where = " AND ".join(conditions) if conditions else "1=1"
        sql = f"SELECT * FROM memories WHERE {where} ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        rows = self.conn.execute(sql, params).fetchall()
        return [self._row_to_entry(r) for r in rows]

    def count(self, type: str = None) -> int:
        if type:
            return self.conn.execute("SELECT COUNT(*) FROM memories WHERE type=?", (type,)).fetchone()[0]
        return self.conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]

    def stats(self) -> Dict:
        """Get storage statistics."""
        total = self.count()
        by_type = {}
        for row in self.conn.execute("SELECT type, COUNT(*) as cnt FROM memories GROUP BY type").fetchall():
            by_type[row["type"]] = row["cnt"]
        by_author = {}
        for row in self.conn.execute("SELECT author, COUNT(*) as cnt FROM memories GROUP BY author").fetchall():
            by_author[row["author"]] = row["cnt"]

        latest = self.conn.execute("SELECT timestamp FROM memories ORDER BY created_at DESC LIMIT 1").fetchone()
        oldest = self.conn.execute("SELECT timestamp FROM memories ORDER BY created_at ASC LIMIT 1").fetchone()

        conflicts = self.conn.execute("SELECT COUNT(*) FROM conflicts").fetchone()[0]

        return {
            "total_entries": total,
            "by_type": by_type,
            "by_author": by_author,
            "conflicts": conflicts,
            "latest": latest["timestamp"] if latest else None,
            "oldest": oldest["timestamp"] if oldest else None,
            "db_path": self.db_path,
            "db_size_kb": round(os.path.getsize(self.db_path) / 1024, 1) if os.path.exists(self.db_path) else 0,
        }

    def delete(self, entry_id: str) -> bool:
        cursor = self.conn.execute("DELETE FROM memories WHERE id=?", (entry_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    def export_jsonl(self) -> str:
        """Export all entries as JSONL string."""
        entries = self.query(limit=999999)
        return "\n".join(json.dumps(e.to_dict()) for e in entries)

    def _row_to_entry(self, row) -> MemoryEntry:
        return MemoryEntry(
            id=row["id"],
            type=row["type"],
            timestamp=row["timestamp"],
            payload=json.loads(row["payload"]),
            author=row["author"],
            version=row["version"],
            tags=json.loads(row["tags"]),
            permissions=json.loads(row["permissions"]),
            hash=row["hash"],
            correlation_id=row["correlation_id"],
        )

    def close(self):
        self.conn.close()


# ============ Conflict Resolution ============
class ConflictResolver:
    """Handles version conflicts using configurable strategies."""

    def __init__(self, storage: CMPStorage):
        self.storage = storage

    def detect_conflict(self, entry: MemoryEntry) -> bool:
        """Check if writing this entry would cause a version conflict."""
        existing_version = self.storage.get_latest_version(entry.id)
        if existing_version is None:
            return False  # New entry, no conflict
        return entry.version <= existing_version

    def resolve_lww(self, entry: MemoryEntry) -> MemoryEntry:
        """Last-Write-Wins: increment version, overwrite."""
        existing = self.storage.get(entry.id)
        if existing:
            entry.version = existing.version + 1
            entry.hash = entry.compute_hash()
        return entry

    def resolve_merge(self, new_entry: MemoryEntry) -> MemoryEntry:
        """Merge: combine non-conflicting payload fields."""
        existing = self.storage.get(new_entry.id)
        if existing:
            merged_payload = {**existing.payload, **new_entry.payload}
            merged_tags = list(set(existing.tags + new_entry.tags))
            new_entry.payload = merged_payload
            new_entry.tags = merged_tags
            new_entry.version = existing.version + 1
            new_entry.hash = new_entry.compute_hash()
        return new_entry

    def log_conflict(self, memory_id: str, versions: List[Dict], strategy: str, resolved_by: str = "system"):
        """Record a conflict for audit trail."""
        self.storage.conn.execute(
            """INSERT INTO conflicts (id, memory_id, versions, resolved_by, resolution_strategy, resolved_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (str(uuid.uuid4()), memory_id, json.dumps(versions), resolved_by, strategy,
             datetime.now(timezone.utc).isoformat())
        )
        self.storage.conn.commit()


# ============ CMP Main Interface ============
class CMP:
    """
    Ceiba Memory Protocol — main interface.

    Usage:
        cmp = CMP()
        entry_id = cmp.write("event", {"description": "something happened"}, tags=["test"])
        results = cmp.query(keywords=["test"])
        cmp.log_task("task-123", "COMPLETED", {"result": "success"})
    """

    def __init__(self, db_path: str = DB_PATH, author: str = "ceiba"):
        self.storage = CMPStorage(db_path)
        self.resolver = ConflictResolver(self.storage)
        self.author = author

    def write(self, type: str, payload: Dict, tags: List[str] = None,
              correlation_id: str = "", author: str = None,
              entry_id: str = None, strategy: str = "lww") -> str:
        """
        Write a memory entry. Handles conflicts automatically.
        Returns the entry ID.
        """
        if type not in VALID_TYPES:
            raise ValueError(f"Invalid type '{type}'. Must be one of: {VALID_TYPES}")

        entry = MemoryEntry.create(
            type=type,
            payload=payload,
            author=author or self.author,
            tags=tags,
            correlation_id=correlation_id,
        )

        if entry_id:
            entry.id = entry_id

        # Check for conflicts
        if self.resolver.detect_conflict(entry):
            existing = self.storage.get(entry.id)
            if existing:
                # Log the conflict
                self.resolver.log_conflict(
                    entry.id,
                    [{"version": existing.version, "author": existing.author},
                     {"version": entry.version, "author": entry.author}],
                    strategy,
                )

                # Resolve
                if strategy == "lww":
                    entry = self.resolver.resolve_lww(entry)
                elif strategy == "merge":
                    entry = self.resolver.resolve_merge(entry)
                else:
                    # Manual — store conflict, return conflict ID
                    conflict_entry = MemoryEntry.create(
                        type="conflict",
                        payload={"memory_id": entry.id, "new_payload": entry.payload},
                        author="system",
                        tags=["conflict", "unresolved"],
                    )
                    self.storage.insert(conflict_entry)
                    return conflict_entry.id

                self.storage.update(entry)
                return entry.id

        # No conflict — insert
        self.storage.insert(entry)
        return entry.id

    def read(self, entry_id: str, agent_id: str = None) -> Optional[MemoryEntry]:
        """Read a memory entry with access control check."""
        entry = self.storage.get(entry_id)
        if not entry:
            return None

        if agent_id:
            allowed = entry.permissions.get("read", [])
            if "*" not in allowed and agent_id not in allowed:
                return None  # Access denied

        return entry

    def query(self, keywords: List[str] = None, types: List[str] = None,
              author: str = None, correlation_id: str = None,
              time_from: str = None, time_to: str = None,
              limit: int = 50) -> List[MemoryEntry]:
        """Query memories with filters."""
        return self.storage.query(
            keywords=keywords, types=types, author=author,
            correlation_id=correlation_id,
            time_from=time_from, time_to=time_to,
            limit=limit,
        )

    def log_task(self, task_id: str, status: str, payload: Dict = None,
                 author: str = None) -> str:
        """
        Convenience method for logging task lifecycle events.
        This is what the gRPC pipeline calls.
        """
        return self.write(
            type="task",
            payload={
                "task_id": task_id,
                "status": status,
                **(payload or {}),
            },
            tags=["task", status.lower(), task_id[:8]],
            correlation_id=task_id,
            author=author or self.author,
        )

    def log_error(self, source: str, message: str, context: Dict = None) -> str:
        """Log an error event."""
        return self.write(
            type="error",
            payload={
                "source": source,
                "message": message,
                **(context or {}),
            },
            tags=["error", source],
        )

    def log_state(self, component: str, state: Dict) -> str:
        """Log a system state snapshot."""
        return self.write(
            type="state",
            payload={"component": component, **state},
            tags=["state", component],
        )

    def task_history(self, task_id: str) -> List[MemoryEntry]:
        """Get full lifecycle history of a task."""
        return self.query(correlation_id=task_id)

    def stats(self) -> Dict:
        return self.storage.stats()

    def verify_all(self) -> Dict:
        """Verify integrity of all entries. Returns corruption report."""
        entries = self.storage.query(limit=999999)
        total = len(entries)
        valid = sum(1 for e in entries if e.verify_integrity())
        corrupted = [e.id for e in entries if not e.verify_integrity()]
        return {
            "total": total,
            "valid": valid,
            "corrupted_count": total - valid,
            "corrupted_ids": corrupted[:20],  # Cap at 20
        }

    def close(self):
        self.storage.close()


# ============ CLI ============
def main():
    parser = argparse.ArgumentParser(description="Ceiba Memory Protocol (CMP)")
    sub = parser.add_subparsers(dest="command", help="Commands")

    # write
    wp = sub.add_parser("write", help="Write a memory entry")
    wp.add_argument("--type", required=True, choices=list(VALID_TYPES))
    wp.add_argument("--payload", required=True, help="JSON payload string")
    wp.add_argument("--tags", default="", help="Comma-separated tags")
    wp.add_argument("--author", default="ceiba")
    wp.add_argument("--correlation", default="", help="Correlation ID (e.g. task ID)")

    # query
    qp = sub.add_parser("query", help="Query memories")
    qp.add_argument("--keywords", default="", help="Comma-separated keywords")
    qp.add_argument("--types", default="", help="Comma-separated types")
    qp.add_argument("--author", default="")
    qp.add_argument("--correlation", default="")
    qp.add_argument("--limit", type=int, default=20)

    # get
    gp = sub.add_parser("get", help="Get a single entry")
    gp.add_argument("id", help="Entry ID")

    # history
    hp = sub.add_parser("history", help="Task lifecycle history")
    hp.add_argument("--task-id", required=True)

    # stats
    sub.add_parser("stats", help="Storage statistics")

    # verify
    sub.add_parser("verify", help="Verify integrity of all entries")

    # export
    ep = sub.add_parser("export", help="Export all entries")
    ep.add_argument("--format", default="jsonl", choices=["jsonl", "json"])

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    cmp = CMP()

    try:
        if args.command == "write":
            payload = json.loads(args.payload)
            tags = [t.strip() for t in args.tags.split(",") if t.strip()]
            entry_id = cmp.write(
                type=args.type, payload=payload, tags=tags,
                author=args.author, correlation_id=args.correlation,
            )
            print(f"Written: {entry_id}")

        elif args.command == "query":
            keywords = [k.strip() for k in args.keywords.split(",") if k.strip()] or None
            types = [t.strip() for t in args.types.split(",") if t.strip()] or None
            results = cmp.query(
                keywords=keywords, types=types,
                author=args.author or None,
                correlation_id=args.correlation or None,
                limit=args.limit,
            )
            for r in results:
                print(f"  [{r.type}] {r.id[:8]}.. {r.timestamp[:19]} by {r.author} — {json.dumps(r.payload)[:100]}")
            print(f"\n  {len(results)} results")

        elif args.command == "get":
            entry = cmp.read(args.id)
            if entry:
                print(json.dumps(entry.to_dict(), indent=2))
                print(f"\nIntegrity: {'VALID' if entry.verify_integrity() else 'CORRUPTED'}")
            else:
                print(f"Not found: {args.id}")

        elif args.command == "history":
            entries = cmp.task_history(args.task_id)
            for e in entries:
                status = e.payload.get("status", "?")
                print(f"  {e.timestamp[:19]} [{status}] {json.dumps(e.payload)[:100]}")
            print(f"\n  {len(entries)} events for task {args.task_id[:8]}..")

        elif args.command == "stats":
            s = cmp.stats()
            print(f"  Total entries: {s['total_entries']}")
            print(f"  By type: {json.dumps(s['by_type'])}")
            print(f"  By author: {json.dumps(s['by_author'])}")
            print(f"  Conflicts: {s['conflicts']}")
            print(f"  Latest: {s['latest']}")
            print(f"  Oldest: {s['oldest']}")
            print(f"  DB size: {s['db_size_kb']} KB")

        elif args.command == "verify":
            report = cmp.verify_all()
            print(f"  Total: {report['total']}")
            print(f"  Valid: {report['valid']}")
            print(f"  Corrupted: {report['corrupted_count']}")
            if report['corrupted_ids']:
                print(f"  IDs: {report['corrupted_ids']}")

        elif args.command == "export":
            if args.format == "jsonl":
                print(cmp.storage.export_jsonl())
            else:
                entries = cmp.query(limit=999999)
                print(json.dumps([e.to_dict() for e in entries], indent=2))

    finally:
        cmp.close()


if __name__ == "__main__":
    main()
