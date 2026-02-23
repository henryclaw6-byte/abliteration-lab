#!/usr/bin/env python3
"""Agent task orchestration with locks, heartbeats, stale recovery, and event logs."""
from __future__ import annotations

import json
import threading
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable, Dict, List, Optional


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_now() -> str:
    return utc_now().isoformat()


def parse_timestamp(timestamp: str) -> datetime:
    parsed = datetime.fromisoformat(timestamp)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


class StaleRecoveryDaemon:
    """Background daemon that periodically recovers stale orchestrator tasks."""

    def __init__(self, orchestrator: "AgentOrchestrator", interval_seconds: int = 30):
        self.orchestrator = orchestrator
        self.interval_seconds = interval_seconds
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    @property
    def is_running(self) -> bool:
        return bool(self._thread and self._thread.is_alive())

    def start(self) -> None:
        if self.is_running:
            return
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._run_loop,
            name="stale-recovery-daemon",
            daemon=True,
        )
        self._thread.start()

    def stop(self, timeout: float = 5.0) -> None:
        if not self._thread:
            return
        self._stop_event.set()
        self._thread.join(timeout=timeout)
        if not self._thread.is_alive():
            self._thread = None

    def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            self.orchestrator.recover_stale_tasks()
            self._stop_event.wait(self.interval_seconds)


@dataclass
class OrchestratedTask:
    """Represents a coordinated unit of work across collaborating agents."""

    task_id: str
    title: str
    payload: Dict
    created_at: str
    created_by: str
    status: str = "pending"
    lock_owner: Optional[str] = None
    lock_acquired_at: Optional[str] = None
    heartbeat_at: Optional[str] = None
    completed_at: Optional[str] = None
    failure_reason: Optional[str] = None


class AgentOrchestrator:
    """Coordinates distributed agents with lock ownership and stale recovery."""

    def __init__(
        self,
        workspace_path: str = "~/.openclaw/workspace",
        stale_after_seconds: int = 90,
        event_hook: Optional[Callable[[Dict], None]] = None,
        recovery_interval_seconds: int = 30,
    ):
        self.workspace = Path(workspace_path).expanduser()
        self.orchestration_dir = self.workspace / "agent_orchestration"
        self.tasks_file = self.orchestration_dir / "tasks.json"
        self.events_file = self.orchestration_dir / "events.jsonl"
        self._lock = threading.RLock()
        self.stale_after = timedelta(seconds=stale_after_seconds)
        self.event_hook = event_hook
        self._recovery_daemon = StaleRecoveryDaemon(
            self, interval_seconds=recovery_interval_seconds
        )
        self.orchestration_dir.mkdir(parents=True, exist_ok=True)
        if not self.tasks_file.exists():
            self._save_tasks({})

    # -------------------------------
    # Public API
    # -------------------------------

    def create_task(self, title: str, payload: Dict, created_by: str) -> OrchestratedTask:
        """Create a new orchestrated task."""
        with self._lock:
            tasks = self._load_tasks()
            task = OrchestratedTask(
                task_id=f"task_{uuid.uuid4().hex[:12]}",
                title=title,
                payload=payload,
                created_at=iso_now(),
                created_by=created_by,
            )
            tasks[task.task_id] = asdict(task)
            self._save_tasks(tasks)
            self._log_event("task_created", task.task_id, created_by, {"title": title})
            return task

    def claim_task(self, task_id: str, agent_id: str) -> bool:
        """Attempt to claim a task lock for an agent."""
        with self._lock:
            tasks = self._load_tasks()
            task = self._get_task_or_raise(tasks, task_id)
            self._recover_stale_lock(task, task_id)
            if task["status"] in {"completed", "failed"}:
                return False
            owner = task.get("lock_owner")
            if owner and owner != agent_id:
                return False
            now = iso_now()
            task["status"] = "in_progress"
            task["lock_owner"] = agent_id
            task["lock_acquired_at"] = now
            task["heartbeat_at"] = now
            self._save_tasks(tasks)
            self._log_event("task_claimed", task_id, agent_id, {})
            return True

    def heartbeat(self, task_id: str, agent_id: str) -> bool:
        """Refresh heartbeat for lock owner."""
        with self._lock:
            tasks = self._load_tasks()
            task = self._get_task_or_raise(tasks, task_id)
            self._recover_stale_lock(task, task_id)
            if task.get("lock_owner") != agent_id:
                return False
            task["heartbeat_at"] = iso_now()
            self._save_tasks(tasks)
            self._log_event("heartbeat", task_id, agent_id, {})
            return True

    def complete_task(self, task_id: str, agent_id: str) -> bool:
        """Mark task complete and release lock."""
        with self._lock:
            tasks = self._load_tasks()
            task = self._get_task_or_raise(tasks, task_id)
            self._recover_stale_lock(task, task_id)
            if task.get("lock_owner") != agent_id:
                return False
            task["status"] = "completed"
            task["completed_at"] = iso_now()
            task["lock_owner"] = None
            task["lock_acquired_at"] = None
            task["heartbeat_at"] = None
            self._save_tasks(tasks)
            self._log_event("task_completed", task_id, agent_id, {})
            return True

    def fail_task(self, task_id: str, agent_id: str, reason: str) -> bool:
        """Mark a task failed and release lock."""
        with self._lock:
            tasks = self._load_tasks()
            task = self._get_task_or_raise(tasks, task_id)
            self._recover_stale_lock(task, task_id)
            if task.get("lock_owner") != agent_id:
                return False
            task["status"] = "failed"
            task["failure_reason"] = reason
            task["lock_owner"] = None
            task["lock_acquired_at"] = None
            task["heartbeat_at"] = None
            self._save_tasks(tasks)
            self._log_event("task_failed", task_id, agent_id, {"reason": reason})
            return True

    def recover_stale_tasks(self) -> List[str]:
        """Release locks for stale in-progress tasks."""
        recovered: List[str] = []
        with self._lock:
            tasks = self._load_tasks()
            for task_id, task in tasks.items():
                if self._recover_stale_lock(task, task_id):
                    recovered.append(task_id)
            self._save_tasks(tasks)
        return recovered

    def get_task(self, task_id: str) -> Dict:
        with self._lock:
            tasks = self._load_tasks()
            task = self._get_task_or_raise(tasks, task_id)
            return dict(task)

    def list_tasks(self) -> List[Dict]:
        with self._lock:
            tasks = self._load_tasks()
            return list(tasks.values())

    def start_recovery_daemon(self) -> None:
        """Start background stale-task recovery (every 30 seconds by default)."""
        self._recovery_daemon.start()

    def stop_recovery_daemon(self, timeout: float = 5.0) -> None:
        """Stop background stale-task recovery."""
        self._recovery_daemon.stop(timeout=timeout)

    def recovery_daemon_running(self) -> bool:
        """Return True if the background recovery daemon is running."""
        return self._recovery_daemon.is_running

    # -------------------------------
    # Internal helpers
    # -------------------------------

    def _load_tasks(self) -> Dict[str, Dict]:
        with open(self.tasks_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_tasks(self, tasks: Dict[str, Dict]) -> None:
        with open(self.tasks_file, "w", encoding="utf-8") as f:
            json.dump(tasks, f, indent=2, sort_keys=True)

    def _log_event(self, event_type: str, task_id: str, actor: str, metadata: Dict) -> None:
        event = {
            "event_id": f"event_{uuid.uuid4().hex[:10]}",
            "timestamp": iso_now(),
            "type": event_type,
            "task_id": task_id,
            "actor": actor,
            "metadata": metadata,
        }
        with open(self.events_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")
        if self.event_hook:
            try:
                self.event_hook(event)
            except Exception as exc:
                fallback = {
                    "event_id": f"event_{uuid.uuid4().hex[:10]}",
                    "timestamp": iso_now(),
                    "type": "event_hook_error",
                    "task_id": task_id,
                    "actor": "orchestrator",
                    "metadata": {"error": str(exc), "source_event_type": event_type},
                }
                with open(self.events_file, "a", encoding="utf-8") as f:
                    f.write(json.dumps(fallback) + "\n")

    def _get_task_or_raise(self, tasks: Dict[str, Dict], task_id: str) -> Dict:
        if task_id not in tasks:
            raise KeyError(f"Unknown task_id: {task_id}")
        return tasks[task_id]

    def _recover_stale_lock(self, task: Dict, task_id: str) -> bool:
        owner = task.get("lock_owner")
        heartbeat = task.get("heartbeat_at")
        if not owner or not heartbeat:
            return False
        heartbeat_dt = parse_timestamp(heartbeat)
        if utc_now() - heartbeat_dt <= self.stale_after:
            return False
        previous_owner = task["lock_owner"]
        task["status"] = "pending"
        task["lock_owner"] = None
        task["lock_acquired_at"] = None
        task["heartbeat_at"] = None
        self._log_event(
            "lock_recovered",
            task_id,
            "orchestrator",
            {"previous_owner": previous_owner},
        )
        return True


def convergence_event_hook(convergence_mind) -> Callable[[Dict], None]:
    """Build an event hook that mirrors orchestrator events into Convergence Mind insights."""

    def _hook(event: Dict) -> None:
        topic = f"orchestration:{event['type']}"
        insight = (
            f"Task {event['task_id']} | actor={event['actor']} "
            f"| metadata={json.dumps(event['metadata'], sort_keys=True)}"
        )
        convergence_mind.record_collaboration(
            participants=[event["actor"]],
            topic=topic,
            insight=insight,
        )

    return _hook


if __name__ == "__main__":
    orchestrator = AgentOrchestrator()
    task = orchestrator.create_task(
        title="Integrate Q00 orchestration protocol",
        payload={"priority": "critical", "domain": "convergence"},
        created_by="henry",
    )
    if orchestrator.claim_task(task.task_id, "codex"):
        orchestrator.heartbeat(task.task_id, "codex")
        orchestrator.complete_task(task.task_id, "codex")
    print("🔥 Agent Orchestrator ready")
    print(json.dumps(orchestrator.get_task(task.task_id), indent=2))
